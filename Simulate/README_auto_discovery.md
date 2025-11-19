# 🔍 Auto-Discovery ESP32 Management System

Hệ thống quản lý ESP32 với auto-discovery và dynamic port allocation.

## 📋 Tổng quan

Hệ thống này cho phép:
- **Auto-Discovery**: Tự động phát hiện ESP32 devices
- **Dynamic Port Allocation**: Cấp port riêng cho mỗi ESP
- **Real-time Monitoring**: Theo dõi trạng thái ESP real-time
- **Individual Control**: Điều khiển từng ESP một cách độc lập

## 🚀 Cách hoạt động

### 1. Discovery Process
```
ESP32 → [Heartbeat] → Port 7000 (Computer)
Computer → [Port Assignment] → ESP32
ESP32 → [Data Communication] → Assigned Port
```

### 2. Port Convention
```python
assigned_port = 7000 + last_ip_octet

Ví dụ:
- ESP IP: 192.168.0.43 → Port: 7043
- ESP IP: 192.168.0.101 → Port: 7101
```

### 3. Heartbeat Protocol
- ESP gửi `HEARTBEAT:ESP_NAME` đến port 7000 mỗi 5 giây
- Computer phản hồi `PORT_ASSIGNED:XXXX`
- ESP chuyển sang giao tiếp trên port được cấp

## 📁 File Structure

```
📂 Auto-Discovery System
├── 📄 auto_discovery_manager.py    # Core discovery engine
├── 📄 auto_discovery_gui.py        # GUI interface
├── 📄 test_auto_discovery.py       # Test system
├── 📄 communication.py             # ESP communication
└── 📄 README_auto_discovery.md     # This file
```

## 🛠️ Installation

### 1. Prerequisites
```bash
# Python 3.8+
# Virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate  # Windows
```

### 2. Dependencies
```bash
pip install pythonosc
# tkinter (usually included with Python)
```

## 📖 Usage

### 1. GUI Mode (Recommended)
```bash
python auto_discovery_gui.py
```

**Workflow:**
1. **Start Discovery**: Click "🚀 Start Discovery"
2. **Monitor ESPs**: Watch ESP list populate automatically
3. **Select ESP**: Click on ESP to control it
4. **Send Commands**: Use control panels

### 2. Test Mode
```bash
python test_auto_discovery.py
```

**Features:**
- ESP simulators for testing
- Both GUI and console modes
- Multiple ESP simulation

### 3. Manager Only
```python
from auto_discovery_manager import AutoDiscoveryManager

manager = AutoDiscoveryManager()
manager.start_discovery()

# Setup callbacks
manager.on_esp_discovered = lambda esp: print(f"Found: {esp['name']}")
manager.on_data_received = lambda data: print(f"Data: {data}")
```

## 🎮 GUI Controls

### Discovery Panel
- **ESP Tree**: Danh sách ESP được phát hiện
- **Status**: Trạng thái kết nối real-time
- **Statistics**: Thống kê heartbeat và data packets

### Control Panel
- **LED Control**: Điều khiển LED (màu, độ sáng, hiệu ứng)
- **Touch Sensor**: Thiết lập threshold
- **Configuration**: Cập nhật IP Resolume

### Monitor Panel
- **System Statistics**: Tổng quan hệ thống
- **Port Assignments**: Mapping port và ESP
- **Discovery Timeline**: Timeline phát hiện ESP

## 🔧 ESP32 Configuration

### Arduino Code
```cpp
#include <WiFi.h>
#include <WiFiUdp.h>

WiFiUDP udp;
String computer_ip = "192.168.0.100";  // IP máy tính
int discovery_port = 7000;
int assigned_port = 0;

void setup() {
    WiFi.begin("SSID", "PASSWORD");
    udp.begin(8888);  // Local port for receiving
}

void loop() {
    sendHeartbeat();
    checkPortAssignment();
    
    if (assigned_port > 0) {
        sendData();  // Send to assigned port
    }
    
    delay(5000);  // 5-second heartbeat
}

void sendHeartbeat() {
    String message = "HEARTBEAT:ESP32_" + WiFi.macAddress();
    udp.beginPacket(computer_ip.c_str(), discovery_port);
    udp.print(message);
    udp.endPacket();
}
```

## 📊 Message Formats

### 1. Heartbeat Messages
```
ESP → Computer: "HEARTBEAT:ESP_NAME"
Computer → ESP: "PORT_ASSIGNED:7043"
```

### 2. Data Messages
```
ESP → Computer: "TOUCH_DATA,3000,LED,255,128,64"
```

### 3. Control Commands
```
Computer → ESP: "LED:1"           # LED on
Computer → ESP: "LEDCTRL:ALL,255,0,0"  # Red color
Computer → ESP: "THRESHOLD:2932"  # Touch threshold
Computer → ESP: "RESOLUME_IP:192.168.0.241"
```

## 🔍 Auto-Discovery Features

### ESP Status Lifecycle
```
🔍 Discovered → 📡 Assigned → 🟢 Connected → 🔴 Offline
```

### Real-time Monitoring
- **Heartbeat tracking**: Monitor ESP liveness
- **Data packet counting**: Track communication
- **Port usage**: Monitor network resources
- **Timeline events**: Discovery history

### Automatic Management
- **Port calculation**: Automatic port assignment
- **Socket creation**: Dynamic port opening
- **Cleanup**: Remove offline ESPs
- **Error handling**: Robust error recovery

## ⚙️ Configuration

### Discovery Settings
```python
class Config:
    discovery_port = 7000           # Port lắng nghe heartbeat
    base_port = 7000               # Base port cho calculation
    heartbeat_timeout = 15.0       # Timeout heartbeat (seconds)
    esp_cleanup_interval = 30      # Cleanup offline ESP (seconds)
```

### Network Settings
```python
# Port range: 7000-7255 (supporting 255 ESPs)
# Each ESP gets unique port based on last IP octet
max_esps = 255
port_range = (7000, 7255)
```

## 🐛 Troubleshooting

### 1. ESP Not Discovered
- **Check network**: ESP và computer cùng subnet
- **Firewall**: Mở port 7000 cho UDP
- **ESP code**: Verify heartbeat sending
- **IP address**: Check computer IP in ESP code

### 2. Port Assignment Failed
- **Port conflict**: Check if calculated port in use
- **Timeout**: Increase heartbeat timeout
- **Network**: UDP packet loss issues

### 3. Data Not Received
- **Port binding**: Assigned port unavailable
- **ESP implementation**: Check data sending code
- **Message format**: Verify data format

### 4. GUI Issues
- **Python version**: Requires Python 3.8+
- **tkinter**: Check tkinter installation
- **Threading**: Close properly to avoid hanging

## 📈 Performance

### Scalability
- **Concurrent ESPs**: Supports up to 255 ESP devices
- **Port allocation**: O(1) port calculation
- **Thread management**: One thread per ESP
- **Memory usage**: Minimal overhead per ESP

### Network Efficiency
- **Heartbeat frequency**: 5-second intervals
- **Port separation**: No cross-ESP interference
- **UDP protocol**: Low latency communication
- **Timeout handling**: Automatic cleanup

## 🔐 Security Considerations

### Network Security
- **Local network**: Designed for local LAN use
- **No authentication**: Open UDP communication
- **Firewall**: Configure appropriate port access
- **IP filtering**: Consider IP whitelist

### Access Control
- **Physical access**: ESP discovery requires network access
- **Command validation**: Implement ESP-side validation
- **Port management**: Monitor port usage

## 📝 Development

### Adding New Commands
```python
# In ESP code
if (command.startsWith("NEW_COMMAND:")) {
    String value = command.substring(12);
    handleNewCommand(value);
}

# In auto_discovery_manager.py
def send_new_command(self, esp_ip, value):
    command = f"NEW_COMMAND:{value}"
    return self.send_command_to_esp(esp_ip, command)
```

### Custom ESP Data
```python
# Extend data parsing in manager
def parse_esp_data(self, data_str):
    # Add custom data formats
    if "CUSTOM_DATA" in data_str:
        return self.parse_custom_data(data_str)
    return self.parse_standard_data(data_str)
```

## 📞 Support

### Debug Information
```python
# Enable verbose logging
manager.debug_mode = True

# Check ESP statistics
stats = manager.get_statistics()
logs = manager.get_logs(50)  # Last 50 logs
```

### Common Patterns
```python
# Check if ESP is online
esp_status = manager.get_esp_status(esp_ip)

# Send command with confirmation
success = manager.send_command_to_esp(esp_ip, "PING")

# Monitor specific ESP
manager.monitor_esp(esp_ip, callback=my_callback)
```

## 🎯 Best Practices

1. **ESP Naming**: Use descriptive ESP names
2. **Error Handling**: Always check command return values
3. **Network Setup**: Use static IPs for ESP devices
4. **Port Management**: Monitor port usage
5. **Cleanup**: Properly stop discovery service

## 📚 Example Workflows

### 1. Basic ESP Control
```python
# Start discovery
manager.start_discovery()

# Wait for ESP
time.sleep(10)

# Control LED
manager.send_command_to_esp("192.168.0.43", "LED:1")
manager.send_command_to_esp("192.168.0.43", "LEDCTRL:ALL,255,0,0")
```

### 2. Multi-ESP Management
```python
esps = manager.get_discovered_esps()
for esp in esps:
    if esp['status'] == 'Connected':
        manager.send_command_to_esp(esp['ip'], "RAINBOW:START")
```

### 3. Real-time Monitoring
```python
def on_data(data):
    if 'touch_value' in data:
        if data['touch_value'] > 3000:
            print(f"Touch detected on {data['esp_name']}")

manager.on_data_received = on_data
```

---

🔍 **Auto-Discovery ESP32 Management System** - Tự động phát hiện và quản lý ESP32 devices với dynamic port allocation.