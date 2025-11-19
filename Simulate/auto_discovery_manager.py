#!/usr/bin/env python3
"""
Auto-Discovery Port Management System
Hệ thống tự động phát hiện ESP và cấp phát port động
"""

import socket
import threading
import time
import json
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import queue

@dataclass
class DiscoveredESP:
    """Thông tin ESP được phát hiện"""
    ip: str
    name: str = ""
    assigned_port: int = 0
    discovery_time: float = 0
    last_heartbeat: float = 0
    status: str = "Discovered"  # Discovered, Assigned, Connected, Offline
    heartbeat_count: int = 0
    data_packets_received: int = 0
    
    def to_dict(self):
        return asdict(self)

class AutoDiscoveryManager:
    """Quản lý auto-discovery và dynamic port allocation"""
    
    DISCOVERY_PORT = 7000
    PORT_BASE = 7000
    HEARTBEAT_TIMEOUT = 15.0  # 15 seconds timeout
    
    def __init__(self, config=None):
        self.config = config
        self.discovered_esps: Dict[str, DiscoveredESP] = {}  # {ip: DiscoveredESP}
        self.active_ports: Dict[int, str] = {}  # {port: esp_ip}
        self.port_sockets: Dict[int, socket.socket] = {}  # {port: socket}
        self.port_threads: Dict[int, threading.Thread] = {}  # {port: thread}
        
        # Discovery socket
        self.discovery_socket = None
        self.discovery_thread = None
        self.running = False
        
        # Cleanup thread
        self.cleanup_thread = None
        
        # Callbacks
        self.on_esp_discovered: Optional[Callable] = None
        self.on_esp_connected: Optional[Callable] = None
        self.on_esp_disconnected: Optional[Callable] = None
        self.on_data_received: Optional[Callable] = None
        
        # Logging
        self.log_messages = []
        self.max_logs = 500
        
        print("🔍 Auto-Discovery Manager initialized")
    
    def start_discovery(self) -> bool:
        """Bắt đầu discovery service"""
        if self.running:
            self.add_log("⚠️ Discovery already running")
            return False
        
        try:
            # Setup discovery socket
            self.discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.discovery_socket.bind(('0.0.0.0', self.DISCOVERY_PORT))
            self.discovery_socket.settimeout(1.0)
            
            self.running = True
            
            # Start discovery listener thread
            self.discovery_thread = threading.Thread(
                target=self._discovery_loop,
                daemon=True,
                name="ESP_Discovery"
            )
            self.discovery_thread.start()
            
            # Start cleanup thread
            self.cleanup_thread = threading.Thread(
                target=self._cleanup_loop,
                daemon=True,
                name="ESP_Cleanup"
            )
            self.cleanup_thread.start()
            
            self.add_log(f"🚀 Discovery service started on port {self.DISCOVERY_PORT}")
            return True
            
        except Exception as e:
            self.add_log(f"❌ Failed to start discovery: {e}")
            self.running = False
            return False
    
    def _discovery_loop(self):
        """Main discovery loop"""
        self.add_log("👂 Discovery listener started")
        
        while self.running:
            try:
                data, addr = self.discovery_socket.recvfrom(1024)
                esp_ip = addr[0]
                
                # Parse heartbeat message
                message = data.decode('utf-8').strip()
                self._process_heartbeat(esp_ip, message)
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    self.add_log(f"❌ Discovery error: {e}")
                break
        
        self.add_log("🔌 Discovery listener stopped")
    
    def _process_heartbeat(self, esp_ip: str, message: str):
        """Xử lý heartbeat từ ESP"""
        current_time = time.time()
        
        try:
            # Parse heartbeat message
            # Expected format: "HEARTBEAT:ESP_NAME" hoặc "HEARTBEAT:192.168.0.43"
            if message.startswith("HEARTBEAT:"):
                esp_name = message.split(":", 1)[1].strip()
                if not esp_name:
                    esp_name = f"ESP_{esp_ip.split('.')[-1]}"
            else:
                # Fallback: treat whole message as ESP name
                esp_name = f"ESP_{esp_ip.split('.')[-1]}"
            
            # Check if ESP already discovered
            if esp_ip in self.discovered_esps:
                # Update existing ESP
                esp_info = self.discovered_esps[esp_ip]
                esp_info.last_heartbeat = current_time
                esp_info.heartbeat_count += 1
                
                # Update status if offline
                if esp_info.status == "Offline":
                    esp_info.status = "Connected" if esp_info.assigned_port > 0 else "Discovered"
                    self.add_log(f"🔄 ESP {esp_ip} ({esp_name}) reconnected")
                    
                    if self.on_esp_connected:
                        self.on_esp_connected(esp_info.to_dict())
            else:
                # New ESP discovered
                assigned_port = self.calculate_port(esp_ip)
                
                esp_info = DiscoveredESP(
                    ip=esp_ip,
                    name=esp_name,
                    assigned_port=assigned_port,
                    discovery_time=current_time,
                    last_heartbeat=current_time,
                    status="Discovered",
                    heartbeat_count=1
                )
                
                self.discovered_esps[esp_ip] = esp_info
                
                self.add_log(f"🔍 New ESP discovered: {esp_name} ({esp_ip}) -> Port {assigned_port}")
                
                # Auto-assign port và setup data channel
                self._setup_esp_data_channel(esp_info)
                
                if self.on_esp_discovered:
                    self.on_esp_discovered(esp_info.to_dict())
        
        except Exception as e:
            self.add_log(f"❌ Heartbeat processing error from {esp_ip}: {e}")
    
    def calculate_port(self, esp_ip: str) -> int:
        """Tính port theo IP ESP"""
        try:
            last_octet = int(esp_ip.split('.')[-1])
            port = self.PORT_BASE + last_octet
            
            if port < 7001 or port > 7255:
                self.add_log(f"⚠️ Port {port} out of range for {esp_ip}")
                return 7000 + (last_octet % 255)  # Fallback
            
            return port
        except Exception as e:
            self.add_log(f"❌ Port calculation error for {esp_ip}: {e}")
            return 7001  # Default fallback
    
    def _setup_esp_data_channel(self, esp_info: DiscoveredESP):
        """Thiết lập kênh data cho ESP"""
        try:
            port = esp_info.assigned_port
            esp_ip = esp_info.ip
            
            # Check if port already in use
            if port in self.active_ports:
                existing_ip = self.active_ports[port]
                if existing_ip != esp_ip:
                    self.add_log(f"⚠️ Port {port} conflict: {existing_ip} vs {esp_ip}")
                    return False
                else:
                    # Same ESP, port already setup
                    return True
            
            # Create data socket for this ESP
            data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            data_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            data_socket.bind(('0.0.0.0', port))
            data_socket.settimeout(1.0)
            
            # Store socket
            self.port_sockets[port] = data_socket
            self.active_ports[port] = esp_ip
            
            # Start data listener thread for this port
            thread = threading.Thread(
                target=self._data_listener,
                args=(port, esp_ip),
                daemon=True,
                name=f"DataListener_{port}"
            )
            thread.start()
            self.port_threads[port] = thread
            
            # Send port assignment to ESP
            self._send_port_assignment(esp_ip, port)
            
            # Update ESP status
            esp_info.status = "Assigned"
            
            self.add_log(f"🌐 Data channel setup: {esp_info.name} ({esp_ip}) on port {port}")
            return True
            
        except Exception as e:
            self.add_log(f"❌ Failed to setup data channel for {esp_ip}: {e}")
            return False
    
    def _send_port_assignment(self, esp_ip: str, port: int):
        """Gửi thông tin port assignment về ESP"""
        try:
            # Send via discovery port first
            message = f"PORT_ASSIGNMENT:{port}"
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(message.encode(), (esp_ip, 4210))  # ESP listen port
            sock.close()
            
            self.add_log(f"📤 Sent port assignment {port} to {esp_ip}")
            
        except Exception as e:
            self.add_log(f"❌ Failed to send port assignment to {esp_ip}: {e}")
    
    def _data_listener(self, port: int, esp_ip: str):
        """Data listener cho port cụ thể"""
        socket_obj = self.port_sockets.get(port)
        if not socket_obj:
            return
        
        self.add_log(f"👂 Data listener started for {esp_ip} on port {port}")
        
        while self.running and port in self.port_sockets:
            try:
                data, addr = socket_obj.recvfrom(4096)
                sender_ip = addr[0]
                
                # Verify sender
                if sender_ip != esp_ip:
                    self.add_log(f"⚠️ Unexpected data from {sender_ip} on port {port} (expected {esp_ip})")
                
                # Update ESP status to connected
                if esp_ip in self.discovered_esps:
                    esp_info = self.discovered_esps[esp_ip]
                    if esp_info.status != "Connected":
                        esp_info.status = "Connected"
                        self.add_log(f"✅ ESP {esp_ip} ({esp_info.name}) data connection established")
                        
                        if self.on_esp_connected:
                            self.on_esp_connected(esp_info.to_dict())
                    
                    esp_info.data_packets_received += 1
                
                # Process data
                self._process_esp_data(esp_ip, port, data, sender_ip)
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    self.add_log(f"❌ Data listener error on port {port}: {e}")
                break
        
        self.add_log(f"🔌 Data listener stopped for port {port}")
    
    def _process_esp_data(self, esp_ip: str, port: int, data: bytes, sender_ip: str):
        """Xử lý dữ liệu từ ESP"""
        try:
            message = data.decode('utf-8').strip()
            
            # Get ESP info
            esp_info = self.discovered_esps.get(esp_ip)
            if not esp_info:
                self.add_log(f"⚠️ Data from unknown ESP: {esp_ip}")
                return
            
            # Parse data
            parsed_data = self._parse_message(message)
            
            if parsed_data and self.on_data_received:
                # Add ESP context
                parsed_data.update({
                    'esp_name': esp_info.name,
                    'esp_ip': esp_ip,
                    'esp_port': port,
                    'sender_ip': sender_ip,
                    'timestamp': time.time()
                })
                
                # Callback
                self.on_data_received(parsed_data)
            
        except Exception as e:
            self.add_log(f"❌ Data processing error from {esp_ip}: {e}")
    
    def _parse_message(self, message: str) -> dict:
        """Parse message từ ESP"""
        try:
            data = {}
            
            # Handle different formats
            if "RawTouch:" in message:
                # Touch data: "RawTouch:1234,Threshold:2500,Value:856"
                parts = message.split(',')
                for part in parts:
                    if ':' in part:
                        key, value = part.split(':', 1)
                        data[key.lower().replace(' ', '_')] = value.strip()
            
            elif message.startswith("STATUS:"):
                # Status message
                data['message_type'] = 'status'
                data['status'] = message.split(':', 1)[1]
            
            elif message.startswith("ACK:"):
                # Acknowledgment
                data['message_type'] = 'acknowledgment'
                data['ack'] = message.split(':', 1)[1]
            
            else:
                # Generic message
                data['message_type'] = 'generic'
                data['message'] = message
            
            return data
            
        except Exception as e:
            return {'message_type': 'error', 'error': str(e), 'raw_message': message}
    
    def _cleanup_loop(self):
        """Cleanup offline ESPs"""
        while self.running:
            try:
                current_time = time.time()
                offline_esps = []
                
                for esp_ip, esp_info in self.discovered_esps.items():
                    # Check heartbeat timeout
                    if current_time - esp_info.last_heartbeat > self.HEARTBEAT_TIMEOUT:
                        if esp_info.status != "Offline":
                            esp_info.status = "Offline"
                            offline_esps.append(esp_ip)
                            
                            self.add_log(f"⚠️ ESP {esp_ip} ({esp_info.name}) went offline (timeout)")
                            
                            if self.on_esp_disconnected:
                                self.on_esp_disconnected(esp_info.to_dict())
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.add_log(f"❌ Cleanup error: {e}")
    
    def send_command_to_esp(self, esp_ip: str, command: str) -> bool:
        """Gửi lệnh đến ESP qua data port"""
        if esp_ip not in self.discovered_esps:
            self.add_log(f"❌ ESP {esp_ip} not found")
            return False
        
        esp_info = self.discovered_esps[esp_ip]
        
        if esp_info.status != "Connected":
            self.add_log(f"⚠️ ESP {esp_ip} not connected (status: {esp_info.status})")
            return False
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            message = command.encode()
            sock.sendto(message, (esp_ip, 4210))  # ESP command port
            sock.close()
            
            self.add_log(f"📤 Command sent to {esp_info.name} ({esp_ip}): {command}")
            return True
            
        except Exception as e:
            self.add_log(f"❌ Failed to send command to {esp_ip}: {e}")
            return False
    
    def broadcast_command(self, command: str) -> Dict[str, bool]:
        """Broadcast lệnh đến tất cả ESP connected"""
        results = {}
        
        for esp_ip, esp_info in self.discovered_esps.items():
            if esp_info.status == "Connected":
                results[esp_ip] = self.send_command_to_esp(esp_ip, command)
        
        success_count = sum(results.values())
        total_count = len(results)
        
        self.add_log(f"📢 Broadcast: {success_count}/{total_count} successful")
        return results
    
    def get_discovered_esps(self) -> List[dict]:
        """Lấy danh sách ESP đã phát hiện"""
        return [esp_info.to_dict() for esp_info in self.discovered_esps.values()]
    
    def get_connected_esps(self) -> List[dict]:
        """Lấy danh sách ESP đang connected"""
        return [esp_info.to_dict() for esp_info in self.discovered_esps.values() 
                if esp_info.status == "Connected"]
    
    def get_statistics(self) -> dict:
        """Lấy thống kê hệ thống"""
        total_esps = len(self.discovered_esps)
        connected_esps = len([esp for esp in self.discovered_esps.values() if esp.status == "Connected"])
        offline_esps = len([esp for esp in self.discovered_esps.values() if esp.status == "Offline"])
        
        total_heartbeats = sum(esp.heartbeat_count for esp in self.discovered_esps.values())
        total_data_packets = sum(esp.data_packets_received for esp in self.discovered_esps.values())
        
        return {
            'discovery_port': self.DISCOVERY_PORT,
            'total_esps': total_esps,
            'connected_esps': connected_esps,
            'offline_esps': offline_esps,
            'active_ports': len(self.active_ports),
            'port_assignments': dict(self.active_ports),
            'total_heartbeats': total_heartbeats,
            'total_data_packets': total_data_packets,
            'uptime': time.time() - (min([esp.discovery_time for esp in self.discovered_esps.values()]) 
                                   if self.discovered_esps else time.time())
        }
    
    def remove_esp(self, esp_ip: str) -> bool:
        """Xóa ESP khỏi hệ thống"""
        if esp_ip not in self.discovered_esps:
            return False
        
        esp_info = self.discovered_esps[esp_ip]
        port = esp_info.assigned_port
        
        # Close port socket
        if port in self.port_sockets:
            self.port_sockets[port].close()
            del self.port_sockets[port]
        
        # Remove from active ports
        if port in self.active_ports:
            del self.active_ports[port]
        
        # Remove ESP
        del self.discovered_esps[esp_ip]
        
        self.add_log(f"🗑️ Removed ESP {esp_info.name} ({esp_ip})")
        return True
    
    def stop_discovery(self):
        """Dừng discovery service"""
        self.running = False
        
        # Close discovery socket
        if self.discovery_socket:
            self.discovery_socket.close()
            self.discovery_socket = None
        
        # Close all data sockets
        for socket_obj in self.port_sockets.values():
            socket_obj.close()
        self.port_sockets.clear()
        self.active_ports.clear()
        
        # Wait for threads
        for thread in [self.discovery_thread, self.cleanup_thread] + list(self.port_threads.values()):
            if thread and thread.is_alive():
                thread.join(timeout=2)
        
        self.port_threads.clear()
        
        self.add_log("🛑 Discovery service stopped")
    
    def add_log(self, message: str):
        """Thêm log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        self.log_messages.append(log_entry)
        if len(self.log_messages) > self.max_logs:
            self.log_messages.pop(0)
        
        print(log_entry)
    
    def get_logs(self, count: int = 50) -> List[str]:
        """Lấy logs gần nhất"""
        return self.log_messages[-count:] if self.log_messages else []

# Demo và test
if __name__ == "__main__":
    def on_esp_discovered(esp_info):
        print(f"🔍 ESP Discovered: {esp_info['name']} ({esp_info['ip']}) -> Port {esp_info['assigned_port']}")
    
    def on_esp_connected(esp_info):
        print(f"✅ ESP Connected: {esp_info['name']} ({esp_info['ip']})")
    
    def on_data_received(data):
        print(f"📥 Data from {data['esp_name']}: {data}")
    
    # Test auto-discovery
    manager = AutoDiscoveryManager()
    manager.on_esp_discovered = on_esp_discovered
    manager.on_esp_connected = on_esp_connected
    manager.on_data_received = on_data_received
    
    print("🚀 Starting Auto-Discovery Demo...")
    
    if manager.start_discovery():
        print("✅ Discovery service started")
        print("💡 Waiting for ESP heartbeats on port 7000...")
        print("📡 ESPs should send: 'HEARTBEAT:ESP_NAME' every 5 seconds")
        print("🌐 Ports will be auto-assigned based on ESP IP")
        print("\\nPress Ctrl+C to stop\\n")
        
        try:
            while True:
                time.sleep(10)
                
                # Print status
                stats = manager.get_statistics()
                print(f"\\n📊 Status: {stats['connected_esps']}/{stats['total_esps']} ESPs connected, "
                      f"{stats['active_ports']} ports active")
                
                esps = manager.get_discovered_esps()
                for esp in esps:
                    print(f"   {esp['name']} ({esp['ip']}) -> Port {esp['assigned_port']} [{esp['status']}]")
        
        except KeyboardInterrupt:
            print("\\n⏹️ Stopping discovery service...")
            manager.stop_discovery()
            print("✅ Demo completed")