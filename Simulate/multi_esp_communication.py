#!/usr/bin/env python3
"""
Multi-ESP Communication Handler
Xử lý giao tiếp đồng thời với nhiều ESP32 mà không bị nghẽn
"""

import socket
import datetime
import threading
import time
import queue
from typing import Optional, Callable, Dict, List
from collections import defaultdict

class MultiESPCommunicationHandler:
    """Xử lý giao tiếp với nhiều ESP32 đồng thời"""
    
    def __init__(self, config):
        self.config = config
        self.log_messages = []
        self.total_packets_sent = 0
        self.total_packets_received = 0
        self.connection_status = "Disconnected"
        
        # Multi-ESP support
        self.esp_devices = {}  # {esp_ip: device_info}
        self.esp_data_queues = defaultdict(queue.Queue)  # {esp_ip: queue}
        self.esp_statistics = defaultdict(lambda: {
            'packets_received': 0,
            'packets_sent': 0,
            'last_seen': None,
            'status': 'Offline'
        })
        
        # Threading for parallel processing
        self.running = False
        self.receive_thread = None
        self.process_threads = {}
        
        # UDP sockets với buffer optimization
        self.udp_socket = None
        self.setup_optimized_socket()
        
        # Callback functions
        self.on_data_update: Optional[Callable] = None
        self.on_esp_status_change: Optional[Callable] = None
        
        # Rate limiting
        self.rate_limiter = {}  # {esp_ip: last_process_time}
        self.min_process_interval = 0.01  # 10ms minimum between processes
        
    def setup_optimized_socket(self):
        """Thiết lập socket với optimization cho nhiều ESP"""
        try:
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Tăng buffer size để tránh mất gói tin
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024*1024)  # 1MB buffer
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 512*1024)   # 512KB send buffer
            
            # Enable port reuse
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Non-blocking mode để tránh hang
            self.udp_socket.settimeout(0.1)
            
            print(f"🌐 Optimized UDP socket setup on port {self.config.osc_port}")
            
        except Exception as e:
            self.add_log(f"Socket setup error: {str(e)}")
            
    def register_esp(self, esp_ip: str, esp_name: str = None) -> bool:
        """Đăng ký ESP32 mới"""
        try:
            if esp_name is None:
                esp_name = f"ESP32_{esp_ip.split('.')[-1]}"
                
            self.esp_devices[esp_ip] = {
                'name': esp_name,
                'ip': esp_ip,
                'registered_at': datetime.datetime.now(),
                'active': True
            }
            
            # Tạo queue riêng cho ESP này
            self.esp_data_queues[esp_ip] = queue.Queue(maxsize=1000)
            
            # Tạo processing thread riêng
            thread = threading.Thread(
                target=self._process_esp_data,
                args=(esp_ip,),
                daemon=True,
                name=f"ESP_Processor_{esp_ip}"
            )
            thread.start()
            self.process_threads[esp_ip] = thread
            
            self.add_log(f"📡 Registered ESP32: {esp_name} ({esp_ip})")
            return True
            
        except Exception as e:
            self.add_log(f"ESP registration error: {str(e)}")
            return False
    
    def start_communication(self):
        """Bắt đầu nhận dữ liệu từ tất cả ESP"""
        if self.running:
            return
            
        try:
            self.udp_socket.bind(('0.0.0.0', self.config.osc_port))
            self.running = True
            
            # Main receive thread
            self.receive_thread = threading.Thread(
                target=self._receive_loop,
                daemon=True,
                name="UDP_Receiver"
            )
            self.receive_thread.start()
            
            # Status monitor thread
            status_thread = threading.Thread(
                target=self._monitor_esp_status,
                daemon=True,
                name="ESP_Monitor"
            )
            status_thread.start()
            
            self.add_log(f"🚀 Multi-ESP communication started on port {self.config.osc_port}")
            
        except Exception as e:
            self.add_log(f"Communication start error: {str(e)}")
            
    def _receive_loop(self):
        """Main loop nhận dữ liệu UDP"""
        while self.running:
            try:
                data, addr = self.udp_socket.recvfrom(4096)
                esp_ip = addr[0]
                
                # Auto-register ESP if not known
                if esp_ip not in self.esp_devices:
                    self.register_esp(esp_ip)
                
                # Rate limiting per ESP
                current_time = time.time()
                if esp_ip in self.rate_limiter:
                    if current_time - self.rate_limiter[esp_ip] < self.min_process_interval:
                        continue  # Skip if too frequent
                
                self.rate_limiter[esp_ip] = current_time
                
                # Queue data cho ESP tương ứng
                try:
                    self.esp_data_queues[esp_ip].put_nowait((data, addr, current_time))
                except queue.Full:
                    # Queue đầy → drop oldest data
                    try:
                        self.esp_data_queues[esp_ip].get_nowait()
                        self.esp_data_queues[esp_ip].put_nowait((data, addr, current_time))
                    except queue.Empty:
                        pass
                
                # Update statistics
                self.esp_statistics[esp_ip]['packets_received'] += 1
                self.esp_statistics[esp_ip]['last_seen'] = current_time
                self.esp_statistics[esp_ip]['status'] = 'Online'
                self.total_packets_received += 1
                
            except socket.timeout:
                continue  # Normal timeout, continue listening
            except Exception as e:
                if self.running:
                    self.add_log(f"Receive error: {str(e)}")
                time.sleep(0.01)
    
    def _process_esp_data(self, esp_ip: str):
        """Xử lý dữ liệu riêng cho từng ESP"""
        esp_queue = self.esp_data_queues[esp_ip]
        
        while self.running:
            try:
                # Get data from queue với timeout
                data, addr, timestamp = esp_queue.get(timeout=1.0)
                
                # Process OSC data
                self._handle_osc_data_from_esp(data, esp_ip, timestamp)
                
                esp_queue.task_done()
                
            except queue.Empty:
                continue  # Timeout, check again
            except Exception as e:
                self.add_log(f"ESP {esp_ip} processing error: {str(e)}")
    
    def _handle_osc_data_from_esp(self, data: bytes, esp_ip: str, timestamp: float):
        """Xử lý dữ liệu OSC từ ESP cụ thể"""
        try:
            # Decode data
            message = data.decode('utf-8').strip()
            
            # Parse data theo format
            esp_data = self._parse_esp_message(message, esp_ip)
            
            if esp_data and self.on_data_update:
                # Add ESP info to data
                esp_data['esp_ip'] = esp_ip
                esp_data['esp_name'] = self.esp_devices[esp_ip]['name']
                esp_data['timestamp'] = timestamp
                
                # Callback to GUI
                self.on_data_update(esp_data)
            
        except Exception as e:
            self.add_log(f"OSC processing error from {esp_ip}: {str(e)}")
    
    def _parse_esp_message(self, message: str, esp_ip: str) -> dict:
        """Parse message từ ESP32"""
        try:
            # Giả sử format: "RawTouch:1234,Threshold:2500,Value:856"
            data = {'esp_ip': esp_ip}
            
            if "RawTouch:" in message:
                parts = message.split(',')
                for part in parts:
                    if "RawTouch:" in part:
                        data['raw_touch'] = part.split(':')[1].strip()
                    elif "Threshold:" in part:
                        data['threshold'] = part.split(':')[1].strip()
                    elif "Value:" in part:
                        data['value'] = part.split(':')[1].strip()
            
            return data
            
        except Exception as e:
            self.add_log(f"Parse error from {esp_ip}: {str(e)}")
            return None
    
    def _monitor_esp_status(self):
        """Monitor trạng thái kết nối của các ESP"""
        while self.running:
            try:
                current_time = time.time()
                timeout_threshold = 5.0  # 5 seconds timeout
                
                for esp_ip, stats in self.esp_statistics.items():
                    if stats['last_seen']:
                        if current_time - stats['last_seen'] > timeout_threshold:
                            if stats['status'] != 'Offline':
                                stats['status'] = 'Offline'
                                if self.on_esp_status_change:
                                    self.on_esp_status_change(esp_ip, 'Offline')
                                self.add_log(f"⚠️ ESP {esp_ip} went offline")
                
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                self.add_log(f"Status monitor error: {str(e)}")
    
    def send_command_to_esp(self, esp_ip: str, command: str) -> bool:
        """Gửi lệnh đến ESP cụ thể"""
        try:
            if esp_ip not in self.esp_devices:
                self.add_log(f"Unknown ESP: {esp_ip}")
                return False
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            message = command.encode()
            sock.sendto(message, (esp_ip, self.config.esp_port))
            sock.close()
            
            self.esp_statistics[esp_ip]['packets_sent'] += 1
            self.total_packets_sent += 1
            self.add_log(f"📤 Sent to {esp_ip}: {command}")
            return True
            
        except Exception as e:
            self.add_log(f"Send error to {esp_ip}: {str(e)}")
            return False
    
    def broadcast_command(self, command: str) -> int:
        """Gửi lệnh đến tất cả ESP"""
        success_count = 0
        for esp_ip in self.esp_devices:
            if self.send_command_to_esp(esp_ip, command):
                success_count += 1
        return success_count
    
    def get_esp_list(self) -> List[dict]:
        """Lấy danh sách ESP và trạng thái"""
        esp_list = []
        for esp_ip, device in self.esp_devices.items():
            stats = self.esp_statistics[esp_ip]
            esp_list.append({
                'ip': esp_ip,
                'name': device['name'],
                'status': stats['status'],
                'packets_received': stats['packets_received'],
                'packets_sent': stats['packets_sent'],
                'last_seen': stats['last_seen']
            })
        return esp_list
    
    def get_performance_stats(self) -> dict:
        """Lấy thống kê hiệu suất"""
        return {
            'total_esp_count': len(self.esp_devices),
            'online_esp_count': sum(1 for stats in self.esp_statistics.values() 
                                   if stats['status'] == 'Online'),
            'total_packets_received': self.total_packets_received,
            'total_packets_sent': self.total_packets_sent,
            'queue_sizes': {esp_ip: q.qsize() 
                           for esp_ip, q in self.esp_data_queues.items()}
        }
    
    def add_log(self, message: str):
        """Thêm log message"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_messages.append(log_entry)
        
        if len(self.log_messages) > self.config.max_log_entries:
            self.log_messages.pop(0)
        
        print(log_entry)  # Also print to console
    
    def stop_communication(self):
        """Dừng communication"""
        self.running = False
        
        if self.udp_socket:
            self.udp_socket.close()
        
        # Wait for threads to finish
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=2)
        
        for thread in self.process_threads.values():
            if thread.is_alive():
                thread.join(timeout=1)
        
        self.add_log("🛑 Multi-ESP communication stopped")