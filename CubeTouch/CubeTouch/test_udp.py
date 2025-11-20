#!/usr/bin/env python3
"""
Simple UDP test script for CubeTouch ESP32
"""

import socket
import time

# ESP32 network configuration
ESP32_IP = "192.168.0.43"
ESP32_PORT = 7000

def test_udp_connection():
    try:
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5.0)
        
        print(f"Testing UDP connection to ESP32 at {ESP32_IP}:{ESP32_PORT}")
        
        # Test basic commands
        test_commands = [
            "CONFIG:1",      # Enable config mode
            "LED:1",         # Enable LEDs
            "255 0 0",       # Set red color
            "0 255 0",       # Set green color  
            "0 0 255",       # Set blue color
            "THRESHOLD:5000", # Set touch threshold
            "CONFIG:0"       # Disable config mode
        ]
        
        for cmd in test_commands:
            print(f"Sending: {cmd}")
            sock.sendto(cmd.encode(), (ESP32_IP, ESP32_PORT))
            time.sleep(2)
            
        print("UDP test completed!")
        
    except Exception as e:
        print(f"UDP test error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    test_udp_connection()