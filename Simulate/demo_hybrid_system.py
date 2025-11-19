#!/usr/bin/env python3
"""
Demo script for Hybrid Cube Touch System
Test hệ thống hybrid với cả classic và auto-discovery modes
"""

import sys
import os
import subprocess
import threading
import time

def print_banner():
    """In banner cho demo"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                   🎮 CUBE TOUCH HYBRID DEMO                  ║
║                                                              ║
║  Tích hợp Classic Mode và Auto-Discovery Mode               ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║  🎹 Classic Mode:    ESP32 cố định với OSC                   ║
║  🔍 Auto-Discovery: Tự động phát hiện multiple ESP          ║
║  🔄 Hybrid Mode:    Kết hợp cả hai chức năng                ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def show_menu():
    """Hiển thị menu lựa chọn"""
    print("\n🎯 CHỌN CHE ĐỘ CHẠY:")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("1. 🎹 Classic Mode Only")
    print("   └─ ESP32 cố định với OSC communication")
    print("   └─ LED control, touch sensor, config mode")
    print("")
    print("2. 🔍 Auto-Discovery Mode Only")
    print("   └─ Tự động phát hiện ESP32 devices")
    print("   └─ Dynamic port allocation")
    print("   └─ Multi-ESP management")
    print("")
    print("3. 🔄 Hybrid Mode (Recommended)")
    print("   └─ Kết hợp cả Classic và Auto-Discovery")
    print("   └─ Switch giữa các mode trong 1 app")
    print("   └─ Full feature set")
    print("")
    print("4. 🧪 Test Auto-Discovery System")
    print("   └─ Chạy test với ESP simulators")
    print("   └─ Demo các tính năng discovery")
    print("")
    print("5. 📚 View Documentation")
    print("6. 🚪 Exit")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

def run_classic_mode():
    """Chạy classic mode"""
    print("\n🎹 Starting Classic Mode...")
    print("Features:")
    print("- LED control with color picker")
    print("- Touch sensor monitoring")
    print("- Config mode for ESP commands")
    print("- Resolume IP configuration")
    
    try:
        subprocess.run([sys.executable, "main.py", "--classic"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running classic mode: {e}")
    except KeyboardInterrupt:
        print("\n⏹️ Classic mode stopped by user")

def run_auto_discovery_mode():
    """Chạy auto-discovery mode"""
    print("\n🔍 Starting Auto-Discovery Mode...")
    print("Features:")
    print("- Automatic ESP32 device discovery")
    print("- Dynamic port allocation (7000 + last IP octet)")
    print("- Multi-ESP management")
    print("- Real-time monitoring")
    
    try:
        subprocess.run([sys.executable, "main.py", "--auto-discovery"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running auto-discovery mode: {e}")
    except KeyboardInterrupt:
        print("\n⏹️ Auto-discovery mode stopped by user")

def run_hybrid_mode():
    """Chạy hybrid mode"""
    print("\n🔄 Starting Hybrid Mode...")
    print("Features:")
    print("- Switch between Classic and Auto-Discovery")
    print("- Unified interface")
    print("- Full feature set from both modes")
    print("- Mode indicator and status")
    
    # Show hybrid instructions
    instructions = """
🔄 HYBRID MODE INSTRUCTIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. App sẽ mở với header có 2 nút mode switcher
2. Click "🎹 Classic Mode" để dùng ESP32 cố định
3. Click "🔍 Auto-Discovery" để discover multiple ESP
4. Status indicators hiển thị trạng thái mỗi mode
5. Data từ cả 2 mode được hiển thị real-time

MODE SWITCHING:
- Classic: Dùng OSC port và ESP IP cố định
- Auto-Discovery: Scan port 7000 cho heartbeats
- Không cần restart app để switch mode
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    print(instructions)
    
    input("📱 Press Enter to start Hybrid Mode...")
    
    try:
        subprocess.run([sys.executable, "main.py", "--hybrid"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running hybrid mode: {e}")
    except KeyboardInterrupt:
        print("\n⏹️ Hybrid mode stopped by user")

def run_test_system():
    """Chạy test system"""
    print("\n🧪 Starting Auto-Discovery Test System...")
    print("This will:")
    print("- Start ESP32 simulators")
    print("- Demo heartbeat discovery")
    print("- Show port allocation")
    print("- Test communication")
    
    try:
        subprocess.run([sys.executable, "test_auto_discovery.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running test system: {e}")
    except KeyboardInterrupt:
        print("\n⏹️ Test system stopped by user")

def show_documentation():
    """Hiển thị documentation"""
    print("\n📚 SYSTEM DOCUMENTATION")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    docs = {
        "File Structure": {
            "main.py": "Entry point với command line arguments",
            "gui.py": "Classic GUI + HybridCubeTouchGUI + EmbeddedAutoDiscoveryGUI", 
            "auto_discovery_manager.py": "Core auto-discovery engine",
            "auto_discovery_gui.py": "Full auto-discovery interface",
            "communication.py": "ESP32 communication handler",
            "config.py": "Application configuration"
        },
        
        "Command Line Usage": {
            "python main.py": "Default hybrid mode",
            "python main.py --classic": "Classic mode only",
            "python main.py --auto-discovery": "Auto-discovery mode only",
            "python main.py --hybrid": "Explicit hybrid mode"
        },
        
        "Auto-Discovery Protocol": {
            "Discovery Port": "7000 (UDP)",
            "Heartbeat": "ESP sends 'HEARTBEAT:ESP_NAME' every 5s",
            "Port Assignment": "Computer responds with 'PORT_ASSIGNED:XXXX'",
            "Port Calculation": "assigned_port = 7000 + last_ip_octet",
            "Data Communication": "ESP uses assigned port for data"
        },
        
        "Integration Features": {
            "Mode Switching": "Runtime switch between Classic/Auto-Discovery",
            "Unified Status": "Both modes show in header status",
            "Shared Resources": "Common config, communication handler",
            "Real-time Updates": "Live data from both modes"
        }
    }
    
    for section, items in docs.items():
        print(f"\n📖 {section}:")
        for key, desc in items.items():
            print(f"   • {key}: {desc}")
    
    print(f"\n📄 Full documentation: README_auto_discovery.md")
    print("🌐 Architecture: Hybrid system supports 255 concurrent ESP devices")

def main():
    """Main function"""
    print_banner()
    
    while True:
        show_menu()
        
        try:
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                run_classic_mode()
            
            elif choice == "2":
                run_auto_discovery_mode()
            
            elif choice == "3":
                run_hybrid_mode()
            
            elif choice == "4":
                run_test_system()
            
            elif choice == "5":
                show_documentation()
            
            elif choice == "6":
                print("\n👋 Goodbye! Thanks for using Cube Touch Hybrid System!")
                break
            
            else:
                print("❌ Invalid choice. Please enter 1-6.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Wait before showing menu again
        input("\n📱 Press Enter to continue...")

if __name__ == "__main__":
    main()