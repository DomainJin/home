#!/usr/bin/env python3
"""
Performance Test Script for Multi-ESP Communication
Kiểm tra hiệu suất khi nhiều ESP gửi dữ liệu đồng thời
"""

import socket
import threading
import time
import random
import statistics
from datetime import datetime

class ESPSimulator:
    """Mô phỏng ESP32 gửi dữ liệu"""
    
    def __init__(self, esp_id, target_ip="127.0.0.1", target_port=7000):
        self.esp_id = esp_id
        self.target_ip = target_ip
        self.target_port = target_port
        self.running = False
        self.packets_sent = 0
        self.send_interval = 0.1  # 100ms between packets
        
    def start_sending(self):
        """Bắt đầu gửi dữ liệu"""
        self.running = True
        thread = threading.Thread(target=self._send_loop, daemon=True)
        thread.start()
        return thread
    
    def _send_loop(self):
        """Loop gửi dữ liệu"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        while self.running:
            try:
                # Tạo dữ liệu mô phỏng
                raw_touch = random.randint(1000, 5000)
                threshold = 2932
                value = random.randint(500, 1500)
                
                message = f"RawTouch:{raw_touch},Threshold:{threshold},Value:{value}"
                
                # Gửi từ IP giả (mô phỏng nhiều ESP)
                fake_ip = f"192.168.0.{100 + self.esp_id}"
                
                sock.sendto(message.encode(), (self.target_ip, self.target_port))
                self.packets_sent += 1
                
                time.sleep(self.send_interval)
                
            except Exception as e:
                print(f"ESP {self.esp_id} send error: {e}")
                break
        
        sock.close()
    
    def stop(self):
        """Dừng gửi"""
        self.running = False

class PerformanceMonitor:
    """Monitor hiệu suất"""
    
    def __init__(self, port=7000):
        self.port = port
        self.running = False
        self.packets_received = 0
        self.bytes_received = 0
        self.receive_times = []
        self.start_time = None
        
    def start_monitoring(self):
        """Bắt đầu monitor"""
        self.running = True
        self.start_time = time.time()
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Tăng buffer để tránh mất gói
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024*1024)
        sock.bind(('0.0.0.0', self.port))
        sock.settimeout(1.0)
        
        print(f"📡 Started monitoring on port {self.port}")
        
        while self.running:
            try:
                data, addr = sock.recvfrom(4096)
                receive_time = time.time()
                
                self.packets_received += 1
                self.bytes_received += len(data)
                self.receive_times.append(receive_time)
                
                # Log mỗi 100 packets
                if self.packets_received % 100 == 0:
                    self._print_stats()
                
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Monitor error: {e}")
                break
        
        sock.close()
        self._print_final_stats()
    
    def _print_stats(self):
        """In thống kê hiện tại"""
        elapsed = time.time() - self.start_time
        pps = self.packets_received / elapsed if elapsed > 0 else 0
        bps = self.bytes_received / elapsed if elapsed > 0 else 0
        
        print(f"📊 Packets: {self.packets_received}, "
              f"Rate: {pps:.1f} pps, "
              f"Bandwidth: {bps/1024:.1f} KB/s")
    
    def _print_final_stats(self):
        """In thống kê cuối"""
        total_time = time.time() - self.start_time
        avg_pps = self.packets_received / total_time if total_time > 0 else 0
        avg_bps = self.bytes_received / total_time if total_time > 0 else 0
        
        print("\\n" + "="*50)
        print("📈 PERFORMANCE REPORT")
        print("="*50)
        print(f"⏱️  Total Time: {total_time:.2f} seconds")
        print(f"📦 Total Packets: {self.packets_received}")
        print(f"📊 Average Rate: {avg_pps:.1f} packets/second")
        print(f"🌐 Average Bandwidth: {avg_bps/1024:.1f} KB/second")
        print(f"💾 Total Data: {self.bytes_received/1024:.1f} KB")
        
        if len(self.receive_times) > 1:
            # Tính jitter (độ biến thiên thời gian)
            intervals = [self.receive_times[i] - self.receive_times[i-1] 
                        for i in range(1, len(self.receive_times))]
            avg_interval = statistics.mean(intervals)
            jitter = statistics.stdev(intervals) if len(intervals) > 1 else 0
            
            print(f"⏰ Average Interval: {avg_interval*1000:.2f} ms")
            print(f"📏 Jitter (StdDev): {jitter*1000:.2f} ms")
        
        # Đánh giá hiệu suất
        if avg_pps > 500:
            print("✅ EXCELLENT: Very high throughput")
        elif avg_pps > 200:
            print("✅ GOOD: High throughput")
        elif avg_pps > 100:
            print("⚠️  MODERATE: Acceptable throughput")
        else:
            print("❌ LOW: Poor throughput - possible bottleneck")
        
        print("="*50)
    
    def stop(self):
        """Dừng monitor"""
        self.running = False

def run_performance_test():
    """Chạy test hiệu suất"""
    print("🧪 MULTI-ESP PERFORMANCE TEST")
    print("="*50)
    
    # Cấu hình test
    esp_count = int(input("Number of ESP32 simulators (1-20): ") or "5")
    test_duration = int(input("Test duration in seconds (10-300): ") or "30")
    packet_rate = float(input("Packets per second per ESP (0.1-10): ") or "1.0")
    
    if esp_count > 20:
        esp_count = 20
        print("⚠️  Limited to 20 ESPs for safety")
    
    print(f"\\n🚀 Starting test with {esp_count} ESP32s")
    print(f"⏱️  Duration: {test_duration} seconds")
    print(f"📡 Rate: {packet_rate} packets/sec per ESP")
    print(f"📊 Expected total rate: {esp_count * packet_rate} packets/sec")
    print("\\nPress Ctrl+C to stop early\\n")
    
    # Tạo monitor
    monitor = PerformanceMonitor()
    monitor_thread = threading.Thread(target=monitor.start_monitoring, daemon=True)
    monitor_thread.start()
    
    time.sleep(2)  # Chờ monitor khởi động
    
    # Tạo ESP simulators
    esp_simulators = []
    esp_threads = []
    
    for i in range(esp_count):
        esp = ESPSimulator(i)
        esp.send_interval = 1.0 / packet_rate  # Convert rate to interval
        esp_simulators.append(esp)
        
        thread = esp.start_sending()
        esp_threads.append(thread)
        
        print(f"📱 Started ESP {i+1}/{esp_count}")
        time.sleep(0.1)  # Stagger starts
    
    try:
        # Chạy test
        print(f"\\n🏃‍♂️ Running test for {test_duration} seconds...")
        time.sleep(test_duration)
        
    except KeyboardInterrupt:
        print("\\n⏹️  Test stopped by user")
    
    # Dừng tất cả
    print("\\n🛑 Stopping ESP simulators...")
    for esp in esp_simulators:
        esp.stop()
    
    # Chờ threads kết thúc
    for thread in esp_threads:
        thread.join(timeout=2)
    
    time.sleep(2)  # Chờ packets cuối
    monitor.stop()
    
    # Tổng kết từ ESP
    total_sent = sum(esp.packets_sent for esp in esp_simulators)
    print(f"\\n📤 Total packets sent by ESPs: {total_sent}")
    print(f"📥 Total packets received by monitor: {monitor.packets_received}")
    
    if total_sent > 0:
        loss_rate = (total_sent - monitor.packets_received) / total_sent * 100
        print(f"📉 Packet loss rate: {loss_rate:.2f}%")
        
        if loss_rate < 1:
            print("✅ Excellent: Very low packet loss")
        elif loss_rate < 5:
            print("✅ Good: Low packet loss")
        elif loss_rate < 15:
            print("⚠️  Moderate: Some packet loss")
        else:
            print("❌ Poor: High packet loss - system overloaded")

def run_stress_test():
    """Chạy stress test với tải cao"""
    print("\\n💪 STRESS TEST MODE")
    print("Testing system limits with high load...")
    
    # Stress test với nhiều ESP và tần suất cao
    esp_counts = [5, 10, 15, 20]
    packet_rates = [1.0, 5.0, 10.0]
    
    results = []
    
    for esp_count in esp_counts:
        for rate in packet_rates:
            print(f"\\n🔥 Testing {esp_count} ESPs at {rate} pps...")
            
            monitor = PerformanceMonitor()
            monitor_thread = threading.Thread(target=monitor.start_monitoring, daemon=True)
            monitor_thread.start()
            
            time.sleep(1)
            
            # Tạo ESPs
            esps = []
            for i in range(esp_count):
                esp = ESPSimulator(i)
                esp.send_interval = 1.0 / rate
                esps.append(esp)
                esp.start_sending()
            
            # Chạy test ngắn
            time.sleep(10)
            
            # Dừng
            for esp in esps:
                esp.stop()
            
            time.sleep(1)
            monitor.stop()
            
            # Ghi kết quả
            total_sent = sum(esp.packets_sent for esp in esps)
            loss_rate = (total_sent - monitor.packets_received) / total_sent * 100 if total_sent > 0 else 0
            
            results.append({
                'esp_count': esp_count,
                'rate': rate,
                'total_rate': esp_count * rate,
                'received_rate': monitor.packets_received / 10,
                'loss_rate': loss_rate
            })
            
            print(f"Result: {monitor.packets_received/10:.1f} pps received, {loss_rate:.1f}% loss")
    
    # Báo cáo stress test
    print("\\n" + "="*60)
    print("📊 STRESS TEST RESULTS")
    print("="*60)
    print("ESPs | Rate | Total Rate | Received | Loss %")
    print("-" * 50)
    
    for r in results:
        print(f"{r['esp_count']:4d} | {r['rate']:4.1f} | {r['total_rate']:9.1f} | {r['received_rate']:8.1f} | {r['loss_rate']:6.1f}")
    
    print("\\n💡 Recommendations:")
    print("- Loss < 5%: System can handle this load")
    print("- Loss 5-15%: Approaching limits")  
    print("- Loss > 15%: System overloaded")

if __name__ == "__main__":
    print("🔬 ESP32 Communication Performance Tester")
    print("="*50)
    
    test_type = input("Test type (1=Normal, 2=Stress): ") or "1"
    
    if test_type == "2":
        run_stress_test()
    else:
        run_performance_test()
    
    input("\\n⏎ Press Enter to exit...")