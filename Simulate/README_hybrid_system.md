# 🎮 Cube Touch Hybrid System - Complete Guide

Hệ thống tích hợp **Classic Mode** và **Auto-Discovery Mode** trong một ứng dụng duy nhất.

## 🌟 Tổng quan

### 🎯 Hybrid Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    HYBRID CUBE TOUCH SYSTEM                │
├─────────────────────────────────────────────────────────────┤
│  🎹 CLASSIC MODE              🔍 AUTO-DISCOVERY MODE        │
│  ├─ ESP32 cố định             ├─ Multiple ESP discovery      │
│  ├─ OSC communication         ├─ Dynamic port allocation    │
│  ├─ LED + Touch control       ├─ Heartbeat protocol         │
│  └─ Config mode               └─ Real-time monitoring       │
│                                                             │
│  🔄 MODE SWITCHING: Runtime switch giữa các modes          │
│  📊 UNIFIED INTERFACE: Single app, multiple capabilities   │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Demo Script (Recommended)
```bash
cd Simulate
python demo_hybrid_system.py
```

**Menu Options:**
- `1` - Classic Mode Only
- `2` - Auto-Discovery Mode Only  
- `3` - Hybrid Mode (Full features)
- `4` - Test với ESP simulators
- `5` - Documentation

### 2. Direct Launch
```bash
# Hybrid mode (default)
python main.py
python main.py --hybrid

# Classic mode only
python main.py --classic

# Auto-Discovery mode only
python main.py --auto-discovery
```

## 🎹 Classic Mode Features

### Core Capabilities
- **LED Control**: Color picker, brightness, effects
- **Touch Sensor**: Real-time monitoring, threshold setting
- **Config Mode**: ESP command mode for LED/sensor config
- **Resolume Integration**: Dynamic IP configuration
- **OSC Server**: Real-time data từ ESP32

### Usage Workflow
1. ESP32 kết nối với IP cố định
2. OSC server lắng nghe trên port 7000
3. Real-time touch data hiển thị
4. LED control và config commands
5. Admin panel cho system monitoring

## 🔍 Auto-Discovery Mode Features

### Core Capabilities
- **Auto Discovery**: Tự động phát hiện ESP32 devices
- **Dynamic Port Allocation**: Port = 7000 + last IP octet
- **Multi-ESP Management**: Quản lý tối đa 255 ESP devices
- **Real-time Monitoring**: Status, heartbeat, data packets
- **Individual Control**: Điều khiển từng ESP riêng biệt

### Discovery Protocol
```
ESP32 → [HEARTBEAT:ESP_NAME] → Port 7000
Computer → [PORT_ASSIGNED:XXXX] → ESP32
ESP32 → [Data Communication] → Assigned Port
```

### Port Calculation
```python
assigned_port = 7000 + last_ip_octet

Examples:
- ESP IP: 192.168.0.43  → Port: 7043
- ESP IP: 192.168.0.101 → Port: 7101
- ESP IP: 10.0.0.15     → Port: 7015
```

## 🔄 Hybrid Mode - Full Integration

### Interface Layout
```
┌─────────────────────────────────────────────────────────────┐
│  🎮 CUBE TOUCH HYBRID     [Classic Mode]     🎹🔍           │
├─────────────────────────────────────────────────────────────┤
│  Status: 🎹 Classic: Ready   🔍 Discovery: Stopped         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Selected Mode Interface]                                  │
│  ├─ Classic: LED control, touch sensor, config             │
│  ├─ Auto-Discovery: ESP list, control panel, monitor       │
│  └─ Runtime switching với header buttons                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Mode Switching
- **Header Buttons**: Click để switch mode instantly
- **Status Indicators**: Real-time status cho cả 2 modes
- **Shared Resources**: Config, communication handlers
- **No Restart Required**: Switch mode without app restart

### Hybrid Features
1. **Unified Configuration**: Single config file cho cả 2 modes
2. **Shared Communication**: Common handler cho ESP communication
3. **Real-time Updates**: Live data từ active mode
4. **Resource Management**: Efficient socket/thread handling
5. **Status Monitoring**: Monitor cả classic ESP và discovered ESPs

## 📁 File Structure

```
Simulate/
├── 📄 main.py                    # Entry point với mode selection
├── 📄 gui.py                     # HybridCubeTouchGUI + Classic GUI
├── 📄 auto_discovery_manager.py  # Core discovery engine
├── 📄 auto_discovery_gui.py      # Full auto-discovery interface
├── 📄 communication.py           # ESP32 communication
├── 📄 config.py                  # Configuration
├── 📄 demo_hybrid_system.py      # Demo script
├── 📄 test_auto_discovery.py     # Test với ESP simulators
└── 📄 README_hybrid_system.md    # This file
```

## 🔧 Configuration

### Application Config
```python
class AppConfig:
    # Classic mode settings
    esp_ip = "192.168.0.100"
    esp_port = 8888
    osc_port = 7000
    resolume_ip = "192.168.0.241"
    
    # Auto-discovery settings  
    discovery_port = 7000
    base_port = 7000
    heartbeat_timeout = 15.0
    esp_cleanup_interval = 30
```

### Network Requirements
- **Classic Mode**: ESP IP cố định, OSC port 7000
- **Auto-Discovery**: UDP port 7000 cho heartbeat
- **Port Range**: 7000-7255 cho ESP communication
- **Firewall**: Mở UDP ports cho communication

## 🎮 Usage Examples

### 1. Classic Mode Workflow
```python
# Start classic mode
python main.py --classic

# Workflow:
# 1. ESP32 connects với fixed IP
# 2. OSC server receives touch data
# 3. Use LED controls, config mode
# 4. Admin panel cho monitoring
```

### 2. Auto-Discovery Workflow
```python
# Start auto-discovery
python main.py --auto-discovery

# Workflow:
# 1. Click "Start Discovery"
# 2. ESP32s send heartbeats → port 7000
# 3. System auto-assigns ports
# 4. Select ESP để control
# 5. Monitor multiple ESP real-time
```

### 3. Hybrid Mode Workflow
```python
# Start hybrid mode
python main.py --hybrid

# Workflow:
# 1. App starts với mode switcher
# 2. Use "🎹 Classic Mode" cho fixed ESP
# 3. Use "🔍 Auto-Discovery" cho multiple ESP
# 4. Switch modes trong runtime
# 5. Monitor status cho cả 2 modes
```

## 🧪 Testing

### 1. Test Auto-Discovery
```bash
python test_auto_discovery.py
# Choose option 1 (GUI Test)
# ESP simulators will connect automatically
```

### 2. Demo System
```bash
python demo_hybrid_system.py
# Interactive demo với all modes
```

### 3. Manual Testing
```bash
# Terminal 1: Start hybrid system
python main.py --hybrid

# Terminal 2: Test ESP simulator
python -c "
import socket, time
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    sock.sendto(b'HEARTBEAT:TEST_ESP', ('127.0.0.1', 7000))
    time.sleep(5)
"
```

## 🔗 ESP32 Integration

### Heartbeat Implementation
```cpp
// ESP32 Arduino Code
#include <WiFi.h>
#include <WiFiUdp.h>

WiFiUDP udp;
String computer_ip = "192.168.0.100";
int discovery_port = 7000;
int assigned_port = 0;

void setup() {
    WiFi.begin("SSID", "PASSWORD");
    udp.begin(8888);
}

void loop() {
    // Send heartbeat every 5 seconds
    String heartbeat = "HEARTBEAT:ESP32_" + WiFi.macAddress();
    udp.beginPacket(computer_ip.c_str(), discovery_port);
    udp.print(heartbeat);
    udp.endPacket();
    
    // Check for port assignment
    int packetSize = udp.parsePacket();
    if (packetSize) {
        String response = udp.readString();
        if (response.startsWith("PORT_ASSIGNED:")) {
            assigned_port = response.substring(14).toInt();
            Serial.println("Got assigned port: " + String(assigned_port));
        }
    }
    
    // Send data to assigned port
    if (assigned_port > 0) {
        sendTouchData();
    }
    
    delay(5000);
}

void sendTouchData() {
    int touch_value = touchRead(T0);
    String data = "TOUCH_DATA," + String(touch_value) + ",LED,255,128,64";
    
    udp.beginPacket(computer_ip.c_str(), assigned_port);
    udp.print(data);
    udp.endPacket();
}
```

## 📊 Performance & Scalability

### System Limits
- **Max ESP Devices**: 255 (port range 7000-7255)
- **Concurrent Connections**: Limited by system resources
- **Memory Usage**: ~2MB per ESP connection
- **Network Load**: ~1KB/s per ESP (heartbeat + data)

### Performance Optimization
- **Threading**: Separate thread per ESP
- **Port Management**: O(1) port calculation
- **Resource Cleanup**: Auto cleanup offline ESPs
- **Memory Management**: Efficient data structures

### Monitoring Tools
```python
# Get system statistics
stats = manager.get_statistics()
print(f"Total ESPs: {stats['total_esps']}")
print(f"Connected: {stats['connected_esps']}")
print(f"Active Ports: {stats['active_ports']}")

# Monitor individual ESP
esp_data = manager.get_esp_data("192.168.0.43")
print(f"Status: {esp_data['status']}")
print(f"Packets: {esp_data['data_packets_received']}")
```

## 🛠️ Development & Extension

### Adding New Commands
```python
# In auto_discovery_manager.py
def send_custom_command(self, esp_ip, param):
    command = f"CUSTOM_COMMAND:{param}"
    return self.send_command_to_esp(esp_ip, command)

# In ESP32 code
if (command.startsWith("CUSTOM_COMMAND:")) {
    String param = command.substring(15);
    handleCustomCommand(param);
}
```

### Custom GUI Components
```python
# In gui.py - HybridCubeTouchGUI
def add_custom_control(self, parent):
    custom_frame = tk.Frame(parent, bg="white")
    # Add custom controls
    return custom_frame
```

### Event Handling
```python
# Setup custom callbacks
manager.on_custom_event = lambda data: print(f"Custom: {data}")
manager.on_esp_data = lambda esp_ip, data: process_data(esp_ip, data)
```

## 🔒 Security & Best Practices

### Network Security
- **Local Network**: Designed for local LAN use
- **Firewall Rules**: Configure appropriate port access
- **IP Filtering**: Consider IP whitelist for production
- **No Authentication**: Current version uses open UDP

### Development Practices
1. **Error Handling**: Always check command return values
2. **Resource Management**: Properly close sockets/threads
3. **Logging**: Use system logs for debugging
4. **Testing**: Test với multiple ESP devices
5. **Documentation**: Document custom modifications

## 📞 Troubleshooting

### Common Issues

**1. ESP Not Discovered**
```bash
# Check:
- Network connectivity (ping ESP)
- Firewall settings (UDP port 7000)
- ESP heartbeat code
- Computer IP in ESP configuration
```

**2. Mode Switching Problems**
```bash
# Check:
- GUI threading issues
- Resource cleanup
- Socket binding conflicts
- Memory usage
```

**3. Port Assignment Failures**
```bash
# Check:
- Port availability (netstat -an)
- Port calculation logic
- UDP packet delivery
- Network configuration
```

**4. Performance Issues**
```bash
# Monitor:
- Thread count (task manager)
- Memory usage
- Network bandwidth
- System load
```

### Debug Tools
```bash
# Enable verbose logging
export DEBUG=1
python main.py --hybrid

# Monitor network traffic
netstat -an | findstr 7000

# Check system resources
tasklist | findstr python
```

## 🎯 Future Enhancements

### Planned Features
1. **Authentication**: User authentication cho ESP access
2. **Database Integration**: Store ESP data và configuration
3. **Web Interface**: Browser-based control panel
4. **Mobile App**: React Native mobile controller
5. **Cloud Integration**: Remote ESP management

### Architecture Improvements
1. **Microservices**: Split into separate services
2. **Message Queue**: Redis/RabbitMQ cho scalability
3. **Load Balancing**: Multiple discovery servers
4. **Monitoring**: Grafana/Prometheus integration
5. **Container Support**: Docker deployment

---

## 📚 Quick Reference

### Command Line Arguments
```bash
python main.py                 # Hybrid mode (default)
python main.py --classic      # Classic mode only
python main.py --auto-discovery  # Auto-discovery only
python main.py --hybrid       # Explicit hybrid mode
```

### Port Usage
```
7000        - Discovery/OSC port
7001-7255   - Auto-assigned ESP ports
8888        - ESP local port (configurable)
```

### File Dependencies
```
main.py → gui.py → auto_discovery_gui.py
       → communication.py
       → auto_discovery_manager.py
       → config.py
```

🎮 **Cube Touch Hybrid System** - Unified ESP32 management với Classic và Auto-Discovery modes! 🚀