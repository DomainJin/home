#!/usr/bin/env python3
"""
Port-Per-ESP Demo and Test Script
Demo và test hệ thống port riêng biệt cho từng ESP
"""

import socket
import threading
import time
import random
from datetime import datetime

class ESPPortSimulator:
    """Mô phỏng ESP32 gửi dữ liệu đến port riêng"""
    
    def __init__(self, esp_id, esp_ip, target_ip="127.0.0.1"):
        self.esp_id = esp_id
        self.esp_ip = esp_ip
        self.target_ip = target_ip
        self.target_port = self.calculate_port()
        self.running = False
        self.packets_sent = 0
        
    def calculate_port(self):
        """Tính port theo quy ước: 7000 + last octet"""
        last_octet = int(self.esp_ip.split('.')[-1])
        return 7000 + last_octet
    
    def start_sending(self, interval=1.0):
        """Bắt đầu gửi dữ liệu"""
        self.running = True
        self.send_interval = interval
        
        thread = threading.Thread(target=self._send_loop, daemon=True,
                                 name=f"ESP_Sim_{self.esp_ip}")
        thread.start()
        return thread
    
    def _send_loop(self):
        """Vòng lặp gửi dữ liệu"""
        print(f"🚀 ESP {self.esp_ip} started sending to port {self.target_port}")
        
        while self.running:
            try:
                # Tạo dữ liệu mô phỏng cảm biến
                raw_touch = random.randint(1000, 5000)
                threshold = 2932
                value = random.randint(500, 1500)
                
                # Tạo message
                message = f"RawTouch:{raw_touch},Threshold:{threshold},Value:{value}"
                
                # Gửi UDP packet
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.bind((self.esp_ip, 0))  # Bind to ESP IP for simulation
                sock.sendto(message.encode(), (self.target_ip, self.target_port))
                sock.close()
                
                self.packets_sent += 1
                
                if self.packets_sent % 10 == 0:
                    print(f"📤 ESP {self.esp_ip} sent {self.packets_sent} packets")
                
                time.sleep(self.send_interval)
                
            except Exception as e:
                print(f"❌ ESP {self.esp_ip} send error: {e}")
                break
    
    def stop(self):
        """Dừng gửi dữ liệu"""
        self.running = False
        print(f"🛑 ESP {self.esp_ip} stopped")

class PortListener:
    """Listener để test nhận dữ liệu trên port riêng"""
    
    def __init__(self, port, esp_ip):
        self.port = port
        self.esp_ip = esp_ip
        self.running = False
        self.packets_received = 0
        self.socket = None
        
    def start_listening(self):
        """Bắt đầu lắng nghe"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('0.0.0.0', self.port))
            self.socket.settimeout(1.0)
            
            self.running = True
            
            thread = threading.Thread(target=self._listen_loop, daemon=True,
                                     name=f"Listener_{self.port}")
            thread.start()
            
            print(f"👂 Started listening for ESP {self.esp_ip} on port {self.port}")
            return thread
            
        except Exception as e:
            print(f"❌ Failed to start listener on port {self.port}: {e}")
            return None
    
    def _listen_loop(self):
        """Vòng lặp lắng nghe"""
        while self.running:
            try:
                data, addr = self.socket.recvfrom(4096)
                sender_ip = addr[0]
                
                # Verify expected ESP
                expected_esp = sender_ip == self.esp_ip
                status = "✅" if expected_esp else "⚠️"
                
                self.packets_received += 1
                
                message = data.decode('utf-8')
                print(f"{status} Port {self.port} received from {sender_ip}: {message[:50]}...")
                
                if self.packets_received % 10 == 0:
                    print(f"📥 Port {self.port} received {self.packets_received} total packets")
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"❌ Port {self.port} error: {e}")
                break
    
    def stop(self):
        """Dừng lắng nghe"""
        self.running = False
        if self.socket:
            self.socket.close()
            self.socket = None
        print(f"🔌 Stopped listening on port {self.port}")

def run_port_per_esp_demo():
    """Chạy demo port-per-ESP"""
    print("🧪 PORT-PER-ESP DEMONSTRATION")
    print("=" * 60)
    
    # Cấu hình ESP test
    esp_configs = [
        ("ESP_043", "192.168.0.43"),  # Port 7043
        ("ESP_044", "192.168.0.44"),  # Port 7044
        ("ESP_100", "192.168.0.100"), # Port 7100
        ("ESP_050", "192.168.0.50"),  # Port 7050
    ]
    
    print("🏗️ Setting up test environment...")
    print("ESP Configuration:")
    print("-" * 40)
    
    esp_simulators = []
    port_listeners = []
    
    # Tạo simulators và listeners
    for name, esp_ip in esp_configs:
        # Tính port theo quy ước
        port = 7000 + int(esp_ip.split('.')[-1])
        print(f"📱 {name} ({esp_ip}) -> Port {port}")
        
        # Tạo ESP simulator
        esp_sim = ESPPortSimulator(name, esp_ip)
        esp_simulators.append(esp_sim)
        
        # Tạo port listener
        listener = PortListener(port, esp_ip)
        port_listeners.append(listener)
    
    print("\\n🚀 Starting listeners...")
    
    # Khởi động listeners
    listener_threads = []
    for listener in port_listeners:
        thread = listener.start_listening()
        if thread:
            listener_threads.append(thread)
    
    time.sleep(2)  # Đợi listeners khởi động
    
    print("\\n📡 Starting ESP simulators...")
    
    # Khởi động ESP simulators
    esp_threads = []
    for esp_sim in esp_simulators:
        thread = esp_sim.start_sending(interval=2.0)  # 2 seconds interval
        esp_threads.append(thread)
        time.sleep(0.5)  # Stagger starts
    
    print("\\n🏃‍♂️ Demo running... (Press Ctrl+C to stop)")
    print("Watch the packet flow between ESP simulators and dedicated ports!")
    print("-" * 60)
    
    try:
        # Chạy demo
        start_time = time.time()
        
        while True:
            time.sleep(10)
            
            # In báo cáo định kỳ
            elapsed = time.time() - start_time
            print(f"\\n📊 Status Report (Running {elapsed:.0f}s):")
            print("-" * 50)
            
            for i, (esp_sim, listener) in enumerate(zip(esp_simulators, port_listeners)):
                print(f"ESP {esp_sim.esp_ip} -> Port {listener.port}: "
                      f"Sent: {esp_sim.packets_sent}, Received: {listener.packets_received}")
            
            total_sent = sum(esp.packets_sent for esp in esp_simulators)
            total_received = sum(listener.packets_received for listener in port_listeners)
            
            print(f"\\n📈 Total: Sent: {total_sent}, Received: {total_received}")
            
            if total_sent > 0:
                success_rate = (total_received / total_sent) * 100
                print(f"✅ Success Rate: {success_rate:.1f}%")
    
    except KeyboardInterrupt:
        print("\\n⏹️ Stopping demo...")
    
    # Cleanup
    print("\\n🧹 Cleaning up...")
    
    # Stop ESP simulators
    for esp_sim in esp_simulators:
        esp_sim.stop()
    
    # Stop listeners
    for listener in port_listeners:
        listener.stop()
    
    # Wait for threads to finish
    for thread in esp_threads + listener_threads:
        if thread and thread.is_alive():
            thread.join(timeout=2)
    
    print("\\n✅ Demo completed!")
    
    # Final statistics
    print("\\n📊 FINAL STATISTICS")
    print("=" * 50)
    
    for esp_sim, listener in zip(esp_simulators, port_listeners):
        print(f"{esp_sim.esp_ip}:{listener.port} - "
              f"Sent: {esp_sim.packets_sent}, "
              f"Received: {listener.packets_received}")
    
    total_sent = sum(esp.packets_sent for esp in esp_simulators)
    total_received = sum(listener.packets_received for listener in port_listeners)
    
    print(f"\\nOverall: {total_sent} sent, {total_received} received")
    
    if total_sent > 0:
        print(f"Success Rate: {(total_received/total_sent)*100:.1f}%")

def test_port_calculation():
    """Test port calculation logic"""
    print("🧮 PORT CALCULATION TEST")
    print("=" * 40)
    
    test_cases = [
        "192.168.0.43",   # -> 7043
        "192.168.0.44",   # -> 7044
        "10.0.0.100",     # -> 7100
        "172.16.1.50",    # -> 7050
        "192.168.1.255",  # -> 7255 (max valid)
        "192.168.1.1",    # -> 7001 (min valid)
    ]
    
    for ip in test_cases:
        last_octet = int(ip.split('.')[-1])
        port = 7000 + last_octet
        
        status = "✅" if 7001 <= port <= 7255 else "❌"
        print(f"{status} {ip} -> Port {port}")
    
    print("\\n💡 Port Convention:")
    print("- Each ESP gets: Port = 7000 + last IP octet")
    print("- Valid range: 7001-7255")
    print("- Example: 192.168.0.43 -> 7043")

def run_load_test():
    """Test tải cao với nhiều ESP"""
    print("\\n💪 LOAD TEST MODE")
    print("Testing high-frequency communication...")
    
    # Test với 10 ESP gửi nhanh
    esp_count = 10
    base_ip = "192.168.0"
    
    simulators = []
    listeners = []
    
    print(f"Creating {esp_count} ESP simulators...")
    
    for i in range(esp_count):
        esp_ip = f"{base_ip}.{43 + i}"
        port = 7043 + i
        
        # ESP simulator
        esp_sim = ESPPortSimulator(f"ESP_{43+i}", esp_ip)
        simulators.append(esp_sim)
        
        # Port listener
        listener = PortListener(port, esp_ip)
        listeners.append(listener)
    
    # Start listeners
    for listener in listeners:
        listener.start_listening()
    
    time.sleep(1)
    
    # Start ESP simulators với tần suất cao
    for esp_sim in simulators:
        esp_sim.start_sending(interval=0.5)  # 2 packets/second each
    
    print(f"\\n📈 Load test running: {esp_count} ESPs @ 2pps = {esp_count*2} total pps")
    
    try:
        time.sleep(30)  # Run for 30 seconds
    except KeyboardInterrupt:
        pass
    
    # Stop everything
    for esp_sim in simulators:
        esp_sim.stop()
    
    for listener in listeners:
        listener.stop()
    
    # Results
    total_sent = sum(esp.packets_sent for esp in simulators)
    total_received = sum(listener.packets_received for listener in listeners)
    
    print(f"\\n📊 Load Test Results:")
    print(f"Total Sent: {total_sent}")
    print(f"Total Received: {total_received}")
    print(f"Success Rate: {(total_received/total_sent)*100:.1f}%" if total_sent > 0 else "N/A")

if __name__ == "__main__":
    print("🌐 Port-Per-ESP Demo & Test Suite")
    print("=" * 60)
    
    while True:
        print("\\nSelect test mode:")
        print("1. 🧮 Port Calculation Test")
        print("2. 🧪 Basic Demo (4 ESPs)")
        print("3. 💪 Load Test (10 ESPs)")
        print("4. 🚪 Exit")
        
        choice = input("\\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            test_port_calculation()
        elif choice == "2":
            run_port_per_esp_demo()
        elif choice == "3":
            run_load_test()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")
        
        input("\\n⏎ Press Enter to continue...")