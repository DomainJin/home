#!/usr/bin/env python3
"""
Test script cho CubeTouch system
Kiểm tra UDP commands, OSC communication và touch responses
"""

import socket
import json
import time
import threading
from pythonosc import udp_client, dispatcher, server
from pythonosc.osc_message import OscMessage

# Network configuration
ESP32_IP = "192.168.0.43"
ESP32_UDP_PORT = 7000
LAPTOP_IP = "192.168.0.159"
LAPTOP_OSC_PORT = 7000

class CubeTouchTester:
    def __init__(self):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.osc_messages = []
        
        # Setup OSC server to receive debug messages
        self.dispatcher = dispatcher.Dispatcher()
        self.dispatcher.map("/debug", self.handle_debug_message)
        
    def handle_debug_message(self, unused_addr, *args):
        """Handle incoming OSC debug messages from ESP32"""
        message = args[0] if args else ""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] OSC DEBUG: {message}")
        self.osc_messages.append((timestamp, message))
    
    def start_osc_server(self):
        """Start OSC server in background thread"""
        def run_server():
            try:
                server_instance = server.osc.ThreadingOSCUDPServer(
                    (LAPTOP_IP, LAPTOP_OSC_PORT), self.dispatcher)
                print(f"OSC Server listening on {LAPTOP_IP}:{LAPTOP_OSC_PORT}")
                server_instance.serve_forever()
            except Exception as e:
                print(f"OSC Server error: {e}")
        
        osc_thread = threading.Thread(target=run_server, daemon=True)
        osc_thread.start()
        time.sleep(1)  # Wait for server to start
    
    def send_udp_command(self, command_dict):
        """Send UDP command to ESP32"""
        try:
            message = json.dumps(command_dict)
            self.udp_socket.sendto(message.encode(), (ESP32_IP, ESP32_UDP_PORT))
            print(f"Sent UDP: {message}")
            return True
        except Exception as e:
            print(f"UDP send error: {e}")
            return False
    
    def test_basic_commands(self):
        """Test basic LED control commands"""
        print("\\n=== Testing Basic Commands ===")
        
        commands = [
            {"cmd": "status"},
            {"cmd": "setColor", "r": 255, "g": 0, "b": 0},  # Red
            {"cmd": "setColor", "r": 0, "g": 255, "b": 0},  # Green
            {"cmd": "setColor", "r": 0, "g": 0, "b": 255},  # Blue
            {"cmd": "setBrightness", "brightness": 128},
            {"cmd": "off"}
        ]
        
        for cmd in commands:
            self.send_udp_command(cmd)
            time.sleep(2)
    
    def test_touch_system_commands(self):
        """Test touch system specific commands"""
        print("\\n=== Testing Touch System Commands ===")
        
        commands = [
            {"cmd": "CONFIG", "state": 1},  # Enable config mode
            {"cmd": "LEDCTRL", "index": "ALL", "r": 255, "g": 255, "b": 255},
            {"cmd": "RAINBOW", "action": "START"},
            {"cmd": "LED", "state": 0},  # Disable LED effects
            {"cmd": "LED", "state": 1},  # Enable LED effects
            {"cmd": "DIR", "direction": 0},  # Reverse direction
            {"cmd": "DIR", "direction": 1},  # Normal direction
            {"cmd": "THRESHOLD", "value": 5000},
            {"cmd": "CONFIG", "state": 0}  # Disable config mode
        ]
        
        for cmd in commands:
            self.send_udp_command(cmd)
            time.sleep(3)
    
    def test_continuous_monitoring(self, duration=30):
        """Monitor OSC messages for specified duration"""
        print(f"\\n=== Monitoring OSC messages for {duration} seconds ===")
        print("Touch the sensor to generate events...")
        
        start_time = time.time()
        while time.time() - start_time < duration:
            time.sleep(0.1)
        
        print(f"\\nReceived {len(self.osc_messages)} OSC messages")
        for timestamp, msg in self.osc_messages[-10:]:  # Show last 10 messages
            print(f"  [{timestamp}] {msg}")
    
    def run_full_test(self):
        """Run complete test suite"""
        print("CubeTouch System Test Starting...")
        print(f"ESP32 Target: {ESP32_IP}:{ESP32_UDP_PORT}")
        print(f"OSC Listening: {LAPTOP_IP}:{LAPTOP_OSC_PORT}")
        
        # Start OSC server
        self.start_osc_server()
        
        # Test basic functionality
        self.test_basic_commands()
        
        # Test touch system
        self.test_touch_system_commands()
        
        # Monitor for touch events
        self.test_continuous_monitoring()
        
        print("\\n=== Test Complete ===")
    
    def __del__(self):
        if hasattr(self, 'udp_socket'):
            self.udp_socket.close()

if __name__ == "__main__":
    # Check if pythonosc is available
    try:
        tester = CubeTouchTester()
        tester.run_full_test()
    except ImportError:
        print("Error: python-osc library not found")
        print("Install with: pip install python-osc")
    except KeyboardInterrupt:
        print("\\nTest interrupted by user")
    except Exception as e:
        print(f"Test error: {e}")