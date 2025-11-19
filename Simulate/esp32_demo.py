#!/usr/bin/env python3
"""
ESP32 Hybrid Code Demo & Instructions
Hướng dẫn compile và deploy ESP32 code với auto-discovery features
"""

import os
import sys

def print_banner():
    """In banner cho ESP32 demo"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                   🎮 ESP32 HYBRID CODE DEMO                 ║
║                                                              ║
║  Tích hợp Auto-Discovery + Classic Mode trong ESP32         ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║  🔍 Auto-Discovery: Heartbeat protocol với dynamic ports    ║
║  🎹 Classic Mode:   Traditional OSC communication           ║
║  🔄 Fallback Logic: Auto switch nếu discovery fails        ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def show_esp32_features():
    """Hiển thị tính năng ESP32"""
    print("\n🚀 **ESP32 HYBRID FEATURES:**")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    features = {
        "🔍 Auto-Discovery Protocol": [
            "• Sends HEARTBEAT:ESP_NAME every 5 seconds to port 7000",
            "• Receives PORT_ASSIGNED:XXXX response",
            "• Switches to assigned port for data communication",
            "• Fallback to classic mode after max attempts"
        ],
        
        "🎹 Classic Mode Fallback": [
            "• Traditional ESP32 IP:Port communication", 
            "• OSC protocol for touch sensor data",
            "• LED control và config mode",
            "• Backward compatibility với existing setup"
        ],
        
        "🎛️ Enhanced Command Handling": [
            "• LED_TEST: RGB sequence test for auto-discovery",
            "• PING/PONG: Connection verification", 
            "• STATUS_REQUEST: Device info reporting",
            "• LEDCTRL:ALL,R,G,B: Direct LED control",
            "• RAINBOW:START: Rainbow effect trigger"
        ],
        
        "📡 Smart Communication": [
            "• Dynamic routing based on assigned port",
            "• Enhanced data format với ESP name và mode info",
            "• Periodic status reporting (every 30s)",
            "• Connection monitoring và retry logic"
        ]
    }
    
    for category, items in features.items():
        print(f"\n{category}:")
        for item in items:
            print(f"   {item}")

def show_configuration_options():
    """Hiển thị configuration options"""
    print("\n⚙️ **CONFIGURATION OPTIONS:**")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    configs = [
        ("ENABLE_AUTO_DISCOVERY", "true", "Enable/disable auto-discovery mode"),
        ("ESP_NAME", "ESP32_CubeTouch01", "Unique identifier cho ESP device"),
        ("HEARTBEAT_INTERVAL", "5000", "Heartbeat frequency in milliseconds"), 
        ("MAX_HEARTBEAT_ATTEMPTS", "5", "Max attempts before fallback"),
        ("discovery_port", "7000", "Port cho heartbeat discovery"),
        ("discoveryLocalPort", "8888", "Local port for discovery responses"),
        ("computer_ip", "192.168.0.159", "Computer IP (auto-detected from gateway)")
    ]
    
    print("\n```cpp")
    for name, value, description in configs:
        print(f"#define {name:<25} {value:<15} // {description}")
    print("```")

def show_arduino_setup():
    """Hiển thị Arduino IDE setup"""
    print("\n🔧 **ARDUINO IDE SETUP:**")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    steps = [
        "1. **Install ESP32 Board Package:**",
        "   • File → Preferences → Additional Board URLs",
        "   • Add: https://dl.espressif.com/dl/package_esp32_index.json", 
        "   • Tools → Board → Board Manager → Search 'ESP32' → Install",
        "",
        "2. **Install Required Libraries:**",
        "   • Tools → Manage Libraries → Install:",
        "     - Adafruit NeoPixel (LED strip control)",
        "     - OSC library for Arduino (OSC communication)",
        "     - WiFi library (built-in với ESP32)",
        "",
        "3. **Select Board Configuration:**", 
        "   • Board: 'ESP32 Dev Module' hoặc board tương ứng",
        "   • Upload Speed: 921600",
        "   • CPU Frequency: 240MHz",
        "   • Flash Size: 4MB",
        "   • Port: Select correct COM port",
        "",
        "4. **Hardware Connections:**",
        "   • LED Strip: Pin 5 (configurable trong LED_PIN)",
        "   • Serial PIC: RX=Pin 33, TX=Pin 26",
        "   • Touch sensor data via UART from PIC",
        "",
        "5. **WiFi Configuration:**",
        "   • SSID: 'Cube Touch' (modify trong code)",
        "   • Password: 'admin123' (modify trong code)",
        "   • Ensure computer và ESP trên cùng network"
    ]
    
    for step in steps:
        print(step)

def show_protocol_flow():
    """Hiển thị protocol flow"""
    print("\n📡 **AUTO-DISCOVERY PROTOCOL FLOW:**")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    flow = """
┌─────────────┐                 ┌─────────────┐
│   ESP32     │                 │  Computer   │
│             │                 │             │
└─────────────┘                 └─────────────┘
       │                               │
       │ 1. HEARTBEAT:ESP_NAME        │
       │ ──────────────────────────>  │ :7000
       │                               │
       │ 2. PORT_ASSIGNED:7043        │
       │ <────────────────────────────│
       │                               │
       │ 3. STATUS:ESP_READY...       │
       │ ──────────────────────────>  │ :7043
       │                               │
       │ 4. Data Communication        │
       │ <────────────────────────>   │ :7043
       │                               │

🔄 Fallback Process (if discovery fails):
   • After MAX_HEARTBEAT_ATTEMPTS (5) → Switch to classic mode
   • Use predefined IP:Port configuration
   • Continue normal operation với OSC protocol
"""
    
    print(flow)

def show_data_formats():
    """Hiển thị data formats"""
    print("\n📊 **DATA FORMATS:**")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    formats = {
        "Heartbeat Message": "HEARTBEAT:ESP32_CubeTouch01",
        "Port Assignment": "PORT_ASSIGNED:7043", 
        "ESP Ready Status": "STATUS:ESP_READY,ESP32_CubeTouch01,192.168.0.43",
        "Enhanced Touch Data": "TOUCH_DATA,3000,LED,255,128,64,STATUS,1,ESP_NAME,ESP32_CubeTouch01,MODE,AUTO",
        "Status Info Response": "STATUS:ESP32_CubeTouch01,192.168.0.43,7043,Connected,Brightness:255,ConfigMode:OFF",
        "Periodic Status": "PERIODIC_STATUS:ESP32_CubeTouch01,Connected,UPTIME:12345,FREE_HEAP:250000"
    }
    
    for name, format_str in formats.items():
        print(f"\n**{name}:**")
        print(f"```\n{format_str}\n```")

def show_testing_workflow():
    """Hiển thị testing workflow"""
    print("\n🧪 **TESTING WORKFLOW:**")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    workflow = [
        "1. **Compile & Upload ESP32 Code:**",
        "   • Open esp32_hybrid.cpp trong Arduino IDE",
        "   • Verify và upload to ESP32 board",
        "   • Monitor Serial output (115200 baud)",
        "",
        "2. **Start Computer Side:**", 
        "   • python main.py --hybrid (start hybrid system)",
        "   • Hoặc python demo_hybrid_system.py → option 3",
        "   • Click 'Auto-Discovery' mode trong GUI",
        "   • Click 'Start Discovery' button",
        "",
        "3. **Verify Auto-Discovery:**",
        "   • ESP32 serial shows: [DISCOVERY] Sent heartbeat",
        "   • Computer GUI shows ESP trong discovered list",
        "   • ESP32 serial shows: [DISCOVERY] ✅ Port assigned",
        "   • Status changes to 'Connected'",
        "",
        "4. **Test Communication:**",
        "   • Select ESP trong GUI list",
        "   • Test commands: LED Test, Rainbow, Ping",
        "   • Verify touch sensor data aparecem",
        "   • Monitor real-time data display",
        "",
        "5. **Test Fallback:**",
        "   • Stop computer discovery service",
        "   • ESP32 should fallback to classic mode",
        "   • Restart computer với classic mode",
        "   • Verify communication continues"
    ]
    
    for step in workflow:
        print(step)

def show_troubleshooting():
    """Hiển thị troubleshooting guide"""
    print("\n🔧 **TROUBLESHOOTING:**")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    issues = {
        "ESP32 không kết nối WiFi": [
            "• Kiểm tra SSID và password trong code",
            "• Verify WiFi network có sẵn",
            "• Check signal strength tại vị trí ESP32",
            "• Reset ESP32 và try again"
        ],
        
        "Heartbeat gửi nhưng không nhận port assignment": [
            "• Kiểm tra computer IP trong ESP32 code", 
            "• Verify port 7000 không bị firewall block",
            "• Check computer có chạy discovery service",
            "• Monitor computer logs cho incoming heartbeats"
        ],
        
        "Port assigned nhưng không có data communication": [
            "• Verify assigned port không conflict",
            "• Check ESP32 chuyển đúng port for data",
            "• Monitor computer logs cho incoming data",
            "• Test với simple ping command"
        ],
        
        "LED hoặc touch sensor không hoạt động": [
            "• Check hardware connections (Pin 5 cho LED)",
            "• Verify PIC UART connection (Pins 33, 26)",
            "• Test LED directly với LED_TEST command",
            "• Monitor serial cho touch data từ PIC"
        ]
    }
    
    for issue, solutions in issues.items():
        print(f"\n**{issue}:**")
        for solution in solutions:
            print(f"   {solution}")

def show_customization_guide():
    """Hiển thị customization guide"""
    print("\n🎨 **CUSTOMIZATION GUIDE:**")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    customizations = [
        "**Device Name & Network:**",
        "```cpp",
        "#define ESP_NAME \"ESP32_YourProjectName\"  // Change device name",
        "const char* ssid = \"YourNetworkName\";      // WiFi SSID", 
        "const char* password = \"YourPassword\";     // WiFi password",
        "String computer_ip = \"192.168.1.100\";     // Target computer IP",
        "```",
        "",
        "**LED Configuration:**",
        "```cpp", 
        "#define LED_PIN     5        // Change LED strip pin",
        "#define NUM_LEDS    150      // Change number of LEDs",
        "int brightness = 255;        // Default brightness (0-255)",
        "```",
        "",
        "**Timing Parameters:**",
        "```cpp",
        "#define HEARTBEAT_INTERVAL 5000    // Heartbeat frequency",
        "#define MAX_HEARTBEAT_ATTEMPTS 5   // Before fallback",
        "#define mainEffectTime 6000        // Effect duration",
        "#define operationTime 2000         // Touch operation time",
        "```",
        "",
        "**Adding Custom Commands:**",
        "```cpp",
        "// In handleAutoDiscoveryCommands() function",
        "else if (strncmp(command, \"CUSTOM_CMD:\", 11) == 0) {",
        "    String param = String(command + 11);",
        "    // Handle your custom command",
        "    Serial.println(\"Custom command: \" + param);",
        "}",
        "```"
    ]
    
    for line in customizations:
        print(line)

def main():
    """Main function"""
    print_banner()
    
    while True:
        print("\n🎯 **ESP32 HYBRID CODE MENU:**")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("1. 🚀 Show ESP32 Features")
        print("2. ⚙️ Configuration Options") 
        print("3. 🔧 Arduino IDE Setup")
        print("4. 📡 Protocol Flow")
        print("5. 📊 Data Formats")
        print("6. 🧪 Testing Workflow")
        print("7. 🔧 Troubleshooting")
        print("8. 🎨 Customization Guide") 
        print("9. 📁 View ESP32 Code File")
        print("10. 🚪 Exit")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        try:
            choice = input("\nEnter your choice (1-10): ").strip()
            
            if choice == "1":
                show_esp32_features()
            elif choice == "2":
                show_configuration_options()
            elif choice == "3":
                show_arduino_setup()
            elif choice == "4":
                show_protocol_flow()
            elif choice == "5":
                show_data_formats()
            elif choice == "6":
                show_testing_workflow()
            elif choice == "7":
                show_troubleshooting()
            elif choice == "8":
                show_customization_guide()
            elif choice == "9":
                if os.path.exists("esp32_hybrid.cpp"):
                    print("\n📁 **ESP32 HYBRID CODE FILE:**")
                    print(f"File: esp32_hybrid.cpp")
                    print(f"Size: {os.path.getsize('esp32_hybrid.cpp')} bytes")
                    print("\nCode ready for Arduino IDE!")
                    print("Copy esp32_hybrid.cpp content to Arduino IDE và compile.")
                else:
                    print("\n❌ esp32_hybrid.cpp not found in current directory")
            elif choice == "10":
                print("\n👋 ESP32 demo completed! Happy coding! 🎮")
                break
            else:
                print("❌ Invalid choice. Please enter 1-10.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\n📱 Press Enter to continue...")

if __name__ == "__main__":
    main()