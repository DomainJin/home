#!/usr/bin/env python3
"""
Simple UDP Test Script for ESP32 LED Controller
This script helps debug UDP communication issues
"""

import socket
import json
import time

def test_udp_connection():
    esp_ip = "192.168.0.43"
    esp_port = 7000
    laptop_ip = "192.168.0.159" 
    laptop_port = 7000
    
    print(f"Testing UDP connection to ESP32...")
    print(f"ESP32: {esp_ip}:{esp_port}")
    print(f"Laptop: {laptop_ip}:{laptop_port}")
    print("-" * 50)
    
    try:
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((laptop_ip, laptop_port))
        sock.settimeout(2.0)  # 2 second timeout
        
        # Test 1: Send a simple status request
        print("Test 1: Sending status request...")
        command = {"cmd": "status"}
        message = json.dumps(command)
        
        sock.sendto(message.encode(), (esp_ip, esp_port))
        print(f"Sent: {message}")
        
        # Try to receive response
        try:
            data, addr = sock.recvfrom(1024)
            response = data.decode()
            print(f"Received from {addr}: {response}")
            print("✓ UDP communication working!")
        except socket.timeout:
            print("✗ No response received (timeout)")
            print("Possible issues:")
            print("  - ESP32 not connected to WiFi")
            print("  - Wrong IP addresses")
            print("  - Firewall blocking UDP")
            print("  - ESP32 UDP server not running")
            
        # Test 2: Send a simple LED command
        print("\nTest 2: Sending LED color command...")
        command = {"cmd": "setColor", "r": 255, "g": 0, "b": 0}
        message = json.dumps(command)
        
        sock.sendto(message.encode(), (esp_ip, esp_port))
        print(f"Sent: {message}")
        
        # Test 3: Listen for any ESP32 messages for a few seconds
        print("\nTest 3: Listening for ESP32 messages for 5 seconds...")
        start_time = time.time()
        messages_received = 0
        
        while time.time() - start_time < 5:
            try:
                data, addr = sock.recvfrom(1024)
                message = data.decode()
                print(f"Received from {addr}: {message}")
                messages_received += 1
            except socket.timeout:
                continue
                
        print(f"Total messages received: {messages_received}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Common issues:")
        print("  - Check network connectivity")
        print("  - Verify IP addresses match ESP32 configuration")
        print("  - Make sure ESP32 is powered on and connected")
        
    finally:
        try:
            sock.close()
        except:
            pass

def ping_test():
    """Test basic network connectivity"""
    import subprocess
    import platform
    
    esp_ip = "192.168.0.43"
    print(f"\nPing test to ESP32 ({esp_ip}):")
    
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "3", esp_ip]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ ESP32 is reachable via ping")
        else:
            print("✗ ESP32 is not reachable via ping")
            print("Check network connection and IP address")
    except Exception as e:
        print(f"Ping test failed: {e}")

if __name__ == "__main__":
    print("ESP32 UDP Connection Test")
    print("=" * 50)
    
    # First test basic connectivity
    ping_test()
    
    # Then test UDP communication
    test_udp_connection()
    
    print("\nTest completed!")