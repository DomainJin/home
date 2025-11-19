#!/usr/bin/env python3
"""
Demo script to test Resolume IP update functionality
Script demo để test tính năng cập nhật IP Resolume
"""

import socket
import time

def send_test_command(esp_ip='192.168.0.43', esp_port=4210, command=''):
    """Gửi lệnh test đến ESP32"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        message = command.encode()
        sock.sendto(message, (esp_ip, esp_port))
        sock.close()
        print(f"✅ Sent: {command}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🧪 Demo test cập nhật IP Resolume")
    print("=" * 50)
    
    # Test commands
    test_commands = [
        "RESOLUME_IP:192.168.1.100",  # IP mới
        "RESOLUME_IP:10.0.0.50",      # IP khác
        "RESOLUME_IP:192.168.0.241",  # Về IP cũ
        "RESOLUME_IP:invalid.ip",     # IP không hợp lệ (để test lỗi)
        "GET_IP_CONFIG"               # Lấy thông tin IP hiện tại
    ]
    
    esp_ip = input("Nhập ESP32 IP (Enter = 192.168.0.43): ").strip()
    if not esp_ip:
        esp_ip = "192.168.0.43"
    
    print(f"📡 Sending commands to ESP32: {esp_ip}:4210")
    print("-" * 50)
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"📤 Test {i}: {cmd}")
        success = send_test_command(esp_ip, 4210, cmd)
        time.sleep(1)  # Chờ 1 giây giữa các lệnh
        print()
    
    print("🏁 Demo completed!")
    print("💡 Check ESP32 serial monitor for responses")

if __name__ == "__main__":
    main()