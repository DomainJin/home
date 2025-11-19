#!/usr/bin/env python3
"""
Port-Per-ESP Communication System
Hệ thống giao tiếp với mỗi ESP32 trên port riêng biệt
Port Convention: 70XX where XX is last 2 digits of ESP IP
Example: ESP 192.168.0.43 -> Port 7043
"""

import socket
import threading
import time
import queue
import re
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ESPDevice:
    """Thông tin ESP Device"""
    name: str
    ip: str
    port: int  # Port máy tính lắng nghe cho ESP này
    esp_port: int = 4210  # Port ESP gửi đến (mặc định)
    status: str = "Offline"
    last_seen: Optional[float] = None
    packets_received: int = 0
    packets_sent: int = 0
    data_queue: Optional[queue.Queue] = None
    socket: Optional[socket.socket] = None
    thread: Optional[threading.Thread] = None

class PortPerESPManager:
    """Quản lý giao tiếp với nhiều ESP thông qua port riêng biệt"""
    
    def __init__(self, config):
        self.config = config
        self.esp_devices: Dict[str, ESPDevice] = {}  # {ip: ESPDevice}
        self.running = False
        
        # Callbacks
        self.on_data_received: Optional[Callable] = None
        self.on_esp_status_change: Optional[Callable] = None
        
        # Logging
        self.log_messages = []
        self.max_logs = 1000
        
        print("🚀 Port-Per-ESP Manager initialized")
    
    def calculate_port(self, esp_ip: str) -> int:
        """Tính port theo IP ESP
        Rule: 70XX where XX = last 2 digits of IP
        Example: 192.168.0.43 -> 7043
        """
        try:
            # Extract last octet
            last_octet = int(esp_ip.split('.')[-1])
            port = 7000 + last_octet
            
            # Validate port range
            if port < 7001 or port > 7255:
                raise ValueError(f"Port {port} out of valid range")
            
            return port
        except Exception as e:
            self.add_log(f"❌ Error calculating port for {esp_ip}: {e}")
            return 7000  # Default fallback
    
    def register_esp(self, esp_ip: str, esp_name: str = None) -> bool:
        """Đăng ký ESP mới với port riêng"""
        try:
            # Validate IP format
            if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', esp_ip):
                raise ValueError("Invalid IP format")
            
            if esp_ip in self.esp_devices:
                self.add_log(f"⚠️ ESP {esp_ip} already registered")
                return False
            
            # Calculate port for this ESP
            listen_port = self.calculate_port(esp_ip)
            
            # Generate name if not provided
            if not esp_name:
                esp_name = f"ESP_{esp_ip.split('.')[-1]}"
            
            # Create ESP device
            esp_device = ESPDevice(
                name=esp_name,
                ip=esp_ip,
                port=listen_port,
                data_queue=queue.Queue(maxsize=500)
            )
            
            self.esp_devices[esp_ip] = esp_device
            
            self.add_log(f"✅ Registered {esp_name} ({esp_ip}) -> Port {listen_port}")
            return True
            
        except Exception as e:
            self.add_log(f"❌ Failed to register ESP {esp_ip}: {e}")
            return False
    
    def start_communication(self) -> bool:
        """Bắt đầu lắng nghe tất cả ESP"""
        if self.running:
            self.add_log("⚠️ Communication already running")
            return False
        
        self.running = True
        success_count = 0
        
        for esp_ip, esp_device in self.esp_devices.items():
            if self._start_esp_listener(esp_device):
                success_count += 1
        
        if success_count > 0:
            self.add_log(f"🚀 Started listening for {success_count}/{len(self.esp_devices)} ESPs")
            return True
        else:
            self.running = False
            self.add_log("❌ Failed to start any ESP listeners")
            return False
    
    def _start_esp_listener(self, esp_device: ESPDevice) -> bool:
        """Bắt đầu lắng nghe cho 1 ESP cụ thể"""
        try:
            # Create UDP socket for this ESP
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(1.0)  # 1 second timeout
            
            # Bind to specific port for this ESP
            sock.bind(('0.0.0.0', esp_device.port))
            esp_device.socket = sock
            
            # Create listening thread
            thread = threading.Thread(
                target=self._listen_for_esp,
                args=(esp_device,),
                daemon=True,
                name=f"ESP_Listener_{esp_device.name}"
            )
            thread.start()
            esp_device.thread = thread
            
            self.add_log(f"📡 Listening for {esp_device.name} on port {esp_device.port}")
            return True
            
        except Exception as e:
            self.add_log(f"❌ Failed to start listener for {esp_device.name}: {e}")
            return False
    
    def _listen_for_esp(self, esp_device: ESPDevice):
        """Lắng nghe dữ liệu từ ESP cụ thể"""
        while self.running:
            try:
                data, addr = esp_device.socket.recvfrom(4096)
                
                # Verify sender IP
                sender_ip = addr[0]
                if sender_ip != esp_device.ip:
                    # Log unexpected sender but continue
                    self.add_log(f"⚠️ Unexpected sender {sender_ip} on port {esp_device.port} (expected {esp_device.ip})")
                
                # Update ESP status
                esp_device.status = "Online"
                esp_device.last_seen = time.time()
                esp_device.packets_received += 1
                
                # Queue data for processing
                try:
                    esp_device.data_queue.put_nowait({
                        'data': data,
                        'sender_ip': sender_ip,
                        'timestamp': time.time(),
                        'esp_device': esp_device
                    })
                except queue.Full:
                    # Drop oldest if queue full
                    try:
                        esp_device.data_queue.get_nowait()
                        esp_device.data_queue.put_nowait({
                            'data': data,
                            'sender_ip': sender_ip,
                            'timestamp': time.time(),
                            'esp_device': esp_device
                        })
                    except queue.Empty:
                        pass
                
                # Process data immediately
                self._process_esp_data(esp_device, data, sender_ip)
                
            except socket.timeout:
                continue  # Normal timeout, continue listening
            except Exception as e:
                if self.running:
                    self.add_log(f"❌ Error listening to {esp_device.name}: {e}")
                break
        
        # Cleanup
        if esp_device.socket:
            esp_device.socket.close()
            esp_device.socket = None
        
        esp_device.status = "Offline"
        self.add_log(f"🔌 Stopped listening for {esp_device.name}")
    
    def _process_esp_data(self, esp_device: ESPDevice, data: bytes, sender_ip: str):
        """Xử lý dữ liệu từ ESP"""
        try:
            message = data.decode('utf-8').strip()
            
            # Parse data according to your protocol
            parsed_data = self._parse_message(message)
            
            if parsed_data and self.on_data_received:
                # Add ESP context to data
                parsed_data.update({
                    'esp_name': esp_device.name,
                    'esp_ip': esp_device.ip,
                    'esp_port': esp_device.port,
                    'sender_ip': sender_ip,
                    'timestamp': time.time()
                })
                
                # Callback to GUI
                self.on_data_received(parsed_data)
            
        except Exception as e:
            self.add_log(f"❌ Error processing data from {esp_device.name}: {e}")
    
    def _parse_message(self, message: str) -> dict:
        """Parse OSC/UDP message từ ESP"""
        try:
            data = {}
            
            # Handle different message formats
            if "RawTouch:" in message:
                # Touch sensor data format: "RawTouch:1234,Threshold:2500,Value:856"
                parts = message.split(',')
                for part in parts:
                    if ':' in part:
                        key, value = part.split(':', 1)
                        data[key.lower().replace(' ', '_')] = value.strip()
            
            elif message.startswith("Resolume IP updated:"):
                # IP update confirmation
                data['message_type'] = 'ip_update_confirm'
                data['message'] = message
            
            else:
                # Generic message
                data['message_type'] = 'generic'
                data['message'] = message
            
            return data
            
        except Exception as e:
            self.add_log(f"❌ Parse error: {e}")
            return {'message_type': 'error', 'message': message}
    
    def send_command_to_esp(self, esp_ip: str, command: str) -> bool:
        """Gửi lệnh đến ESP cụ thể"""
        if esp_ip not in self.esp_devices:
            self.add_log(f"❌ ESP {esp_ip} not registered")
            return False
        
        esp_device = self.esp_devices[esp_ip]
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            message = command.encode('utf-8')
            sock.sendto(message, (esp_ip, esp_device.esp_port))
            sock.close()
            
            esp_device.packets_sent += 1
            self.add_log(f"📤 Sent to {esp_device.name}: {command}")
            return True
            
        except Exception as e:
            self.add_log(f"❌ Failed to send to {esp_device.name}: {e}")
            return False
    
    def broadcast_command(self, command: str) -> Dict[str, bool]:
        """Gửi lệnh đến tất cả ESP"""
        results = {}
        for esp_ip in self.esp_devices:
            results[esp_ip] = self.send_command_to_esp(esp_ip, command)
        
        success_count = sum(results.values())
        self.add_log(f"📢 Broadcast: {success_count}/{len(results)} successful")
        return results
    
    def get_esp_list(self) -> List[dict]:
        """Lấy danh sách ESP với thông tin chi tiết"""
        esp_list = []
        for esp_ip, esp_device in self.esp_devices.items():
            esp_list.append({
                'name': esp_device.name,
                'ip': esp_ip,
                'port': esp_device.port,
                'status': esp_device.status,
                'last_seen': esp_device.last_seen,
                'packets_received': esp_device.packets_received,
                'packets_sent': esp_device.packets_sent,
                'queue_size': esp_device.data_queue.qsize() if esp_device.data_queue else 0
            })
        return esp_list
    
    def get_performance_stats(self) -> dict:
        """Lấy thống kê tổng quan"""
        total_received = sum(esp.packets_received for esp in self.esp_devices.values())
        total_sent = sum(esp.packets_sent for esp in self.esp_devices.values())
        online_count = sum(1 for esp in self.esp_devices.values() if esp.status == "Online")
        
        return {
            'total_esp_count': len(self.esp_devices),
            'online_esp_count': online_count,
            'offline_esp_count': len(self.esp_devices) - online_count,
            'total_packets_received': total_received,
            'total_packets_sent': total_sent,
            'ports_in_use': [esp.port for esp in self.esp_devices.values()],
            'active_connections': [(esp.ip, esp.port) for esp in self.esp_devices.values() if esp.status == "Online"]
        }
    
    def unregister_esp(self, esp_ip: str) -> bool:
        """Hủy đăng ký ESP"""
        if esp_ip not in self.esp_devices:
            return False
        
        esp_device = self.esp_devices[esp_ip]
        
        # Stop thread and close socket
        if esp_device.socket:
            esp_device.socket.close()
        
        if esp_device.thread and esp_device.thread.is_alive():
            # Thread will stop automatically when socket closes
            esp_device.thread.join(timeout=2)
        
        # Remove from devices
        del self.esp_devices[esp_ip]
        
        self.add_log(f"🗑️ Unregistered {esp_device.name}")
        return True
    
    def stop_communication(self):
        """Dừng tất cả giao tiếp"""
        self.running = False
        
        # Close all sockets and stop threads
        for esp_device in self.esp_devices.values():
            if esp_device.socket:
                esp_device.socket.close()
                esp_device.socket = None
            
            esp_device.status = "Offline"
        
        # Wait for threads to finish
        for esp_device in self.esp_devices.values():
            if esp_device.thread and esp_device.thread.is_alive():
                esp_device.thread.join(timeout=2)
        
        self.add_log("🛑 All communication stopped")
    
    def add_log(self, message: str):
        """Thêm log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        self.log_messages.append(log_entry)
        if len(self.log_messages) > self.max_logs:
            self.log_messages.pop(0)
        
        print(log_entry)  # Also print to console
    
    def get_logs(self, count: int = 50) -> List[str]:
        """Lấy logs gần nhất"""
        return self.log_messages[-count:] if self.log_messages else []

# Example usage and demo
if __name__ == "__main__":
    class DemoConfig:
        pass
    
    # Test the port calculation
    manager = PortPerESPManager(DemoConfig())
    
    test_ips = [
        "192.168.0.43",   # -> Port 7043
        "192.168.0.44",   # -> Port 7044  
        "192.168.0.100",  # -> Port 7100
        "10.0.0.45",      # -> Port 7045
    ]
    
    print("🧪 Port Calculation Test:")
    print("-" * 40)
    for ip in test_ips:
        port = manager.calculate_port(ip)
        print(f"ESP {ip} -> Port {port}")
    
    print("\n✅ Port-Per-ESP system ready!")
    print("Each ESP will have its dedicated port for communication.")