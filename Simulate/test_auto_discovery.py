#!/usr/bin/env python3
"""
Auto-Discovery System Test
Test tổng hợp hệ thống Auto-Discovery với ESP32
"""

import tkinter as tk
from auto_discovery_gui import AutoDiscoveryGUI
import threading
import time
import socket

class AutoDiscoverySystemTest:
    """Test hoàn chỉnh hệ thống Auto-Discovery"""
    
    def __init__(self):
        print("🔍 Auto-Discovery System Test")
        print("=" * 50)
        
        # Test with configuration
        class TestConfig:
            discovery_port = 7000
            base_port = 7000
            heartbeat_timeout = 15.0  # 15 seconds timeout
            esp_cleanup_interval = 30  # Check for offline ESP every 30s
        
        self.config = TestConfig()
        
    def create_esp_simulator(self, esp_name, esp_ip):
        """Tạo simulator ESP"""
        def esp_simulator():
            print(f"🔧 Starting ESP simulator: {esp_name} ({esp_ip})")
            
            try:
                # Create socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(1.0)
                
                # Computer IP (localhost for test)
                computer_ip = "127.0.0.1"  # Localhost for testing
                discovery_port = 7000
                
                # Send heartbeats every 5 seconds
                while True:
                    try:
                        # Send heartbeat message
                        heartbeat_msg = f"HEARTBEAT:{esp_name}"
                        sock.sendto(heartbeat_msg.encode(), (computer_ip, discovery_port))
                        print(f"💓 {esp_name}: Sent heartbeat")
                        
                        # Try to receive port assignment
                        try:
                            data, addr = sock.recvfrom(1024)
                            response = data.decode()
                            
                            if response.startswith("PORT_ASSIGNED:"):
                                assigned_port = int(response.split(":")[1])
                                print(f"📡 {esp_name}: Got assigned port {assigned_port}")
                                
                                # Now can send data to assigned port
                                self.send_test_data(esp_name, esp_ip, assigned_port, computer_ip)
                        
                        except socket.timeout:
                            # No response, continue heartbeat
                            pass
                        
                        # Wait 5 seconds before next heartbeat
                        time.sleep(5)
                        
                    except Exception as e:
                        print(f"❌ {esp_name}: Error in heartbeat: {e}")
                        time.sleep(5)
                        
            except Exception as e:
                print(f"❌ {esp_name}: Failed to start: {e}")
        
        # Start simulator in thread
        thread = threading.Thread(target=esp_simulator, daemon=True)
        thread.start()
        return thread
    
    def send_test_data(self, esp_name, esp_ip, assigned_port, computer_ip):
        """Gửi dữ liệu test sau khi được cấp port"""
        def data_sender():
            try:
                data_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                
                # Send some test touch data
                for i in range(5):
                    touch_value = 3000 + (i * 100)  # Simulate touch values
                    
                    # Simulate OSC-like message format
                    test_data = f"TOUCH_DATA,{touch_value},LED,128,128,255"
                    data_sock.sendto(test_data.encode(), (computer_ip, assigned_port))
                    
                    print(f"📊 {esp_name}: Sent data - touch:{touch_value}")
                    time.sleep(2)
                
            except Exception as e:
                print(f"❌ {esp_name}: Data sending error: {e}")
        
        # Start data sender in thread
        data_thread = threading.Thread(target=data_sender, daemon=True)
        data_thread.start()
    
    def run_gui_test(self):
        """Chạy test với GUI"""
        print("🖥️ Starting GUI test...")
        
        # Create main window
        root = tk.Tk()
        
        # Start GUI
        app = AutoDiscoveryGUI(root, self.config)
        
        # Create some ESP simulators after a short delay
        def start_simulators():
            time.sleep(2)  # Wait for GUI to initialize
            
            print("🚀 Starting ESP simulators...")
            
            # Create multiple ESP simulators
            esp_configs = [
                ("ESP32_Cube01", "127.0.0.1"),  # Simulate different IPs
                ("ESP32_Touch02", "127.0.0.2"),
                ("ESP32_LED03", "127.0.0.3"),
                ("ESP32_Sensor04", "127.0.0.4")
            ]
            
            for esp_name, esp_ip in esp_configs:
                time.sleep(1)  # Stagger startup
                self.create_esp_simulator(esp_name, esp_ip)
            
            print("✅ All ESP simulators started!")
            print("💡 Use GUI to start discovery and watch ESPs connect")
        
        # Start simulators in background
        sim_thread = threading.Thread(target=start_simulators, daemon=True)
        sim_thread.start()
        
        # Show instructions
        instructions = """
🔍 Auto-Discovery System Test
════════════════════════════════════════
Instructions:
1. Click 'Start Discovery' to begin
2. ESP simulators will send heartbeats
3. Watch them appear in the discovery panel
4. Select an ESP to control it
5. Use control panels to send commands

ESP Simulators Running:
• ESP32_Cube01 (127.0.0.1)
• ESP32_Touch02 (127.0.0.2)  
• ESP32_LED03 (127.0.0.3)
• ESP32_Sensor04 (127.0.0.4)

Each will get a port: 7000 + last IP octet
For example: 127.0.0.1 → Port 7001
"""
        print(instructions)
        
        # Run GUI
        try:
            root.mainloop()
        finally:
            app.auto_update_running = False
            if hasattr(app, 'manager'):
                app.manager.stop_discovery()
            print("👋 Test completed!")
    
    def run_console_test(self):
        """Chạy test console đơn giản"""
        print("⌨️ Console test mode")
        print("Starting auto-discovery manager...")
        
        from auto_discovery_manager import AutoDiscoveryManager
        
        manager = AutoDiscoveryManager(self.config)
        
        # Setup callbacks
        def on_esp_discovered(esp_info):
            print(f"🔍 ESP discovered: {esp_info['name']} at {esp_info['ip']}")
        
        def on_esp_connected(esp_info):
            print(f"✅ ESP connected: {esp_info['name']} on port {esp_info['assigned_port']}")
        
        def on_data_received(data):
            print(f"📊 Data from {data.get('esp_name', 'Unknown')}: {data}")
        
        manager.on_esp_discovered = on_esp_discovered
        manager.on_esp_connected = on_esp_connected  
        manager.on_data_received = on_data_received
        
        # Start discovery
        if manager.start_discovery():
            print("🚀 Discovery started on port 7000")
            
            # Start some ESP simulators
            time.sleep(1)
            esp_configs = [
                ("ESP32_Test01", "127.0.0.1"),
                ("ESP32_Test02", "127.0.0.2")
            ]
            
            for esp_name, esp_ip in esp_configs:
                self.create_esp_simulator(esp_name, esp_ip)
                time.sleep(0.5)
            
            # Run for 60 seconds
            try:
                print("📡 Monitoring for 60 seconds...")
                print("Press Ctrl+C to stop early")
                
                for i in range(60):
                    time.sleep(1)
                    
                    # Show statistics every 10 seconds
                    if i % 10 == 0:
                        stats = manager.get_statistics()
                        print(f"📈 Stats: {stats.get('total_esps', 0)} ESPs, "
                              f"{stats.get('connected_esps', 0)} connected")
                
            except KeyboardInterrupt:
                print("\n⏹️ Stopped by user")
            
            finally:
                manager.stop_discovery()
                print("✅ Discovery stopped")
        
        else:
            print("❌ Failed to start discovery")

def main():
    """Main function"""
    print("🔍 Auto-Discovery System Test")
    print("Choose test mode:")
    print("1. GUI Test (recommended)")
    print("2. Console Test")
    print("3. Exit")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        test = AutoDiscoverySystemTest()
        
        if choice == "1":
            test.run_gui_test()
        elif choice == "2":
            test.run_console_test()
        elif choice == "3":
            print("👋 Goodbye!")
            return
        else:
            print("❌ Invalid choice")
            main()
            
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    main()