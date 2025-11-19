# 🎮 ESP32 Hybrid Code - Complete Implementation

## 📋 Tổng quan

ESP32 code đã được cập nhật hoàn toàn để tích hợp với **Hybrid Cube Touch System**, hỗ trợ cả **Auto-Discovery** và **Classic Mode**.

## 🔄 **Hybrid Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    ESP32 HYBRID SYSTEM                     │
├─────────────────────────────────────────────────────────────┤
│  🔍 AUTO-DISCOVERY MODE          🎹 CLASSIC MODE           │
│  ├─ Heartbeat protocol           ├─ Fixed IP:Port          │
│  ├─ Dynamic port assignment      ├─ OSC communication      │ 
│  ├─ Enhanced commands            ├─ Traditional commands   │
│  └─ Auto fallback               └─ Backward compatibility │
│                                                             │
│  🎛️ SHARED FEATURES: LED Control, Touch Sensor, Config    │
│  📡 SMART ROUTING: Dynamic communication based on mode     │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 **Key Features**

### 🔍 **Auto-Discovery Protocol**
- **Heartbeat Transmission**: Gửi `HEARTBEAT:ESP_NAME` mỗi 5 giây đến port 7000
- **Dynamic Port Assignment**: Nhận `PORT_ASSIGNED:XXXX` từ computer
- **Smart Fallback**: Tự động chuyển sang classic mode nếu discovery fails
- **Enhanced Commands**: LED_TEST, PING/PONG, STATUS_REQUEST

### 🎹 **Classic Mode Compatibility** 
- **Backward Compatible**: Hoạt động với existing setup
- **OSC Protocol**: Traditional communication method
- **Fixed Configuration**: Predefined IP:Port settings
- **Seamless Transition**: Auto fallback từ discovery mode

### 🎛️ **Enhanced Command System**
- **Universal Commands**: Hoạt động trong cả 2 modes
- **Mode-Specific Commands**: Auto-discovery enhanced features
- **Smart Routing**: Dynamic destination based on assigned port
- **Rich Data Format**: Enhanced với ESP name và mode info

## 📁 **File Structure**

```
📄 esp32_hybrid.cpp           # Main ESP32 code với hybrid features
📄 esp32.cpp                  # Original code (for reference)  
📄 esp32_demo.py              # Demo script với instructions
📄 README_ESP32_hybrid.md     # This documentation
```

## ⚙️ **Configuration**

### **Auto-Discovery Settings**
```cpp
#define ENABLE_AUTO_DISCOVERY true        // Enable/disable auto-discovery
#define ESP_NAME "ESP32_CubeTouch01"      // Unique ESP identifier
#define HEARTBEAT_INTERVAL 5000           // Heartbeat frequency (ms)
#define MAX_HEARTBEAT_ATTEMPTS 5          // Max attempts before fallback
```

### **Network Configuration**
```cpp
const char* ssid = "Cube Touch";          // WiFi SSID
const char* password = "admin123";         // WiFi password
String computer_ip = "192.168.0.159";     // Computer IP (auto-detected)
const unsigned int discovery_port = 7000; // Discovery port
```

### **Hardware Configuration**
```cpp
#define LED_PIN     5                     // LED strip pin
#define NUM_LEDS    150                   // Number of LEDs
unsigned int localUdpPort = 4210;        // Local UDP port
unsigned int discoveryLocalPort = 8888;  // Discovery local port
```

## 📡 **Communication Protocols**

### **1. Auto-Discovery Flow**
```
ESP32 → HEARTBEAT:ESP_NAME → Computer:7000
Computer → PORT_ASSIGNED:7043 → ESP32
ESP32 → STATUS:ESP_READY,... → Computer:7043
ESP32 ↔ Data Communication ↔ Computer:7043
```

### **2. Enhanced Data Format**
```cpp
// Touch data với enhanced information
String enhanced_data = "TOUCH_DATA," + String(latestValue) + 
                      ",LED," + String(last_r) + "," + String(last_g) + "," + String(last_b) + 
                      ",STATUS," + String(latestStatus) + 
                      ",ESP_NAME," + String(ESP_NAME) + 
                      ",MODE," + (discovery_mode ? "AUTO" : "CLASSIC");
```

### **3. Status Reporting**
```cpp
// Periodic status (every 30 seconds)
String status_report = "PERIODIC_STATUS:" + String(ESP_NAME) + "," + 
                       device_status + "," + 
                       "UPTIME:" + String(millis() / 1000) + "," +
                       "FREE_HEAP:" + String(ESP.getFreeHeap());
```

## 🎛️ **Command Reference**

### **Auto-Discovery Commands**
| Command | Description | Example |
|---------|-------------|---------|
| `LED_TEST` | RGB sequence test | Cycles through R→G→B→OFF |
| `PING` | Connection test | Returns `PONG:ESP_NAME` |
| `STATUS_REQUEST` | Device info | Returns full status info |
| `RAINBOW:START` | Rainbow effect | Starts rainbow LED effect |

### **Universal Commands** (Both Modes)
| Command | Description | Example |
|---------|-------------|---------|
| `CONFIG:1` | Enable config mode | `CONFIG:1` (enable) |
| `LEDCTRL:ALL,255,0,0` | Direct LED control | All LEDs red |
| `LED:1` | LED on/off | `LED:1` (on), `LED:0` (off) |
| `DIR:1` | LED direction | `DIR:1` (up), `DIR:0` (down) |
| `THRESHOLD:2932` | Touch threshold | Sets touch threshold |
| `RESOLUME_IP:192.168.0.241` | Update Resolume IP | Changes target IP |

## 🔧 **Arduino IDE Setup**

### **1. Board Configuration**
```
Board: ESP32 Dev Module
Upload Speed: 921600
CPU Frequency: 240MHz  
Flash Size: 4MB
Partition Scheme: Default
```

### **2. Required Libraries**
```
- Adafruit NeoPixel (LED strip control)
- OSC library for Arduino (OSC communication)
- WiFi library (built-in with ESP32)
```

### **3. Hardware Connections**
```
LED Strip Data Pin: GPIO 5 (configurable)
PIC UART RX: GPIO 33
PIC UART TX: GPIO 26
Baud Rate: 9600 (PIC), 115200 (Serial Monitor)
```

## 🧪 **Testing Workflow**

### **1. Upload ESP32 Code**
```bash
1. Open esp32_hybrid.cpp in Arduino IDE
2. Verify & Upload to ESP32 board
3. Open Serial Monitor (115200 baud)
4. Verify WiFi connection và mode selection
```

### **2. Start Computer System**
```bash
# Start hybrid system
python main.py --hybrid

# Or use demo
python demo_hybrid_system.py
# Choose option 3 (Hybrid Mode)
```

### **3. Test Auto-Discovery**
```bash
1. Click "Auto-Discovery Mode" trong GUI
2. Click "Start Discovery" 
3. ESP32 serial: [DISCOVERY] Sent heartbeat
4. Computer GUI: ESP appears trong list
5. ESP32 serial: [DISCOVERY] ✅ Port assigned
```

### **4. Test Commands**
```bash
1. Select ESP trong GUI list
2. Test: LED Test, Rainbow, Ping
3. Verify touch sensor data
4. Check real-time data display
```

## 📊 **Debug & Monitoring**

### **ESP32 Serial Output**
```
🎮 ESP32 Cube Touch Hybrid System Starting...
Device Name: ESP32_CubeTouch01
Auto-Discovery: ENABLED
✅ WiFi connected!
Local IP: 192.168.0.43
🔍 AUTO-DISCOVERY MODE
Discovery target: 192.168.0.159:7000
[DISCOVERY] Sent heartbeat #1: HEARTBEAT:ESP32_CubeTouch01
[DISCOVERY] ✅ Port assigned: 7043
[AUTO-DISCOVERY:7043] Received: LED_TEST
[AUTO-DISCOVERY] LED test completed
```

### **Computer Side Monitoring**
```python
# In auto-discovery GUI
📊 Statistics: 1 ESP discovered, 1 connected
📡 Port Assignments: Port 7043: ESP32_CubeTouch01
🔍 Timeline: [12:34:56] ESP discovered: ESP32_CubeTouch01
```

## 🔧 **Troubleshooting**

### **Common Issues & Solutions**

**1. ESP32 không gửi heartbeat:**
```cpp
// Check WiFi connection
if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected!");
}

// Verify discovery mode
if (!discovery_mode) {
    Serial.println("Auto-discovery disabled");
}
```

**2. Heartbeat gửi nhưng không nhận port:**
```python
# Check computer firewall (Windows)
netsh advfirewall firewall add rule name="CubeTouch UDP" dir=in action=allow protocol=UDP localport=7000

# Check computer IP
ipconfig  # Windows
ifconfig  # Linux/Mac
```

**3. Port assigned nhưng no data:**
```cpp
// Verify assigned port usage
if (port_assigned && assigned_port > 0) {
    Serial.printf("Using assigned port: %d\n", assigned_port);
} else {
    Serial.println("Using classic mode");
}
```

## 🎨 **Customization Examples**

### **1. Change Device Name**
```cpp
#define ESP_NAME "ESP32_MyProject"
```

### **2. Modify LED Configuration**
```cpp
#define LED_PIN     12      // Different pin
#define NUM_LEDS    200     // More LEDs
int brightness = 128;       // Lower default brightness
```

### **3. Add Custom Command**
```cpp
void handleAutoDiscoveryCommands(char* command) {
    // ... existing commands ...
    
    else if (strncmp(command, "CUSTOM_FLASH:", 13) == 0) {
        int count = atoi(command + 13);
        for (int i = 0; i < count; i++) {
            // Flash LEDs
            for (int j = 0; j < NUM_LEDS; j++) {
                strip.setPixelColor(j, strip.Color(255, 255, 255));
            }
            strip.show();
            delay(200);
            
            for (int j = 0; j < NUM_LEDS; j++) {
                strip.setPixelColor(j, strip.Color(0, 0, 0));
            }
            strip.show();
            delay(200);
        }
        Serial.printf("[CUSTOM] Flashed %d times\n", count);
    }
}
```

### **4. Network Auto-Detection**
```cpp
void setup() {
    // ... WiFi connection ...
    
    // Auto-detect computer IP từ gateway
    IPAddress gateway = WiFi.gatewayIP();
    computer_ip = gateway.toString();
    
    // Or scan network for discovery service
    // scanForDiscoveryService();
}
```

## 📈 **Performance Characteristics**

### **Memory Usage**
```
Flash: ~1.2MB (ESP32 code + libraries)
RAM: ~50KB (static) + ~20KB (dynamic)
Heap: ~250KB free (typical)
```

### **Timing Specifications**
```
Heartbeat Interval: 5000ms
Discovery Timeout: 25 seconds (5 attempts × 5s)
Fallback Time: <1 second
Touch Response: <50ms
LED Update: 13ms (operationTime/NUM_LEDS)
```

### **Network Performance**
```
Heartbeat Size: ~30 bytes
Touch Data Size: ~120 bytes (enhanced format)
Status Report: ~150 bytes
Network Overhead: Minimal UDP headers
```

## 🔐 **Security Considerations**

### **Network Security**
- **Local Network Only**: Designed cho LAN usage
- **No Encryption**: Plain UDP communication
- **Open Discovery**: Any device có thể gửi heartbeat
- **IP Validation**: Basic IP format checking

### **Best Practices**
```cpp
// Validate command lengths
if (strlen(command) > MAX_COMMAND_LENGTH) {
    Serial.println("Command too long, ignoring");
    return;
}

// Rate limiting cho commands
static unsigned long last_command = 0;
if (millis() - last_command < MIN_COMMAND_INTERVAL) {
    return; // Ignore rapid commands
}
```

## 📚 **Advanced Features**

### **1. Multi-Network Support**
```cpp
// Support multiple computer IPs
String computer_ips[] = {"192.168.0.159", "192.168.1.100", "10.0.0.100"};
int current_ip_index = 0;

void tryNextComputer() {
    current_ip_index = (current_ip_index + 1) % 3;
    computer_ip = computer_ips[current_ip_index];
    heartbeat_attempts = 0; // Reset attempts
}
```

### **2. Enhanced Error Recovery**
```cpp
void checkConnectionHealth() {
    static unsigned long last_data_sent = 0;
    
    if (millis() - last_data_sent > CONNECTION_TIMEOUT) {
        Serial.println("Connection timeout, attempting recovery");
        if (port_assigned) {
            // Try to re-establish discovery
            port_assigned = false;
            device_status = "Reconnecting";
        }
    }
}
```

### **3. Firmware OTA Updates**
```cpp
#include <ArduinoOTA.h>

void setupOTA() {
    ArduinoOTA.setHostname(ESP_NAME);
    ArduinoOTA.begin();
    
    ArduinoOTA.onStart([]() {
        Serial.println("OTA Start");
    });
    
    ArduinoOTA.onEnd([]() {
        Serial.println("OTA End");
    });
}

void loop() {
    ArduinoOTA.handle(); // Handle OTA updates
    // ... rest of loop code ...
}
```

## 🎯 **Integration Examples**

### **1. Home Assistant Integration**
```yaml
# configuration.yaml
sensor:
  - platform: udp
    host: 192.168.0.43
    port: 8888
    name: "Cube Touch Sensor"
    
switch:
  - platform: command_line
    switches:
      cube_led:
        command_on: 'echo "LED:1" | nc -u 192.168.0.43 4210'
        command_off: 'echo "LED:0" | nc -u 192.168.0.43 4210'
```

### **2. Node-RED Flow**
```json
[
    {
        "id": "udp-in",
        "type": "udp in",
        "port": "7043",
        "name": "Cube Touch Data"
    },
    {
        "id": "udp-out", 
        "type": "udp out",
        "host": "192.168.0.43",
        "port": "4210",
        "name": "Cube Commands"
    }
]
```

## 📞 **Support & Resources**

### **Documentation Files**
- `README_hybrid_system.md` - Complete hybrid system guide
- `README_auto_discovery.md` - Auto-discovery documentation  
- `README_ESP32_hybrid.md` - This ESP32 guide

### **Demo Scripts**
- `esp32_demo.py` - Interactive ESP32 demo
- `demo_hybrid_system.py` - Full system demo
- `test_auto_discovery.py` - Auto-discovery testing

### **Development Tools**
```bash
# Run ESP32 demo
python esp32_demo.py

# Test full system
python demo_hybrid_system.py

# Monitor network traffic
netstat -an | findstr 7000  # Windows
ss -tulpn | grep 7000       # Linux
```

---

## 🚀 **Quick Start Summary**

1. **📁 Copy** `esp32_hybrid.cpp` to Arduino IDE
2. **⚙️ Configure** WiFi credentials và ESP name
3. **📤 Upload** to ESP32 board
4. **🖥️ Start** computer hybrid system
5. **🔍 Enable** Auto-Discovery mode
6. **✅ Verify** ESP appears trong discovered list
7. **🎮 Test** commands và touch sensor data

**🎮 ESP32 Hybrid System** - Intelligent device discovery với seamless fallback! 🚀