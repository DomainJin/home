# CubeTouch - Hệ thống Touch với OSC và UDP Debug

## Tổng quan chuyển đổi

File `main1.ino` đã được chuyển đổi thành cấu trúc PlatformIO với FreeRTOS để tối ưu hiệu năng và khả năng mở rộng.

## Cấu trúc hệ thống mới

### 1. Thư viện được cập nhật (platformio.ini)

```ini
lib_deps =
    adafruit/Adafruit NeoPixel@^1.15.2
    bblanchon/ArduinoJson@^7.0.4
    CNMAT/OSC@^1.3.7  # Thư viện OSC từ CNMAT cho PlatformIO
```

### 2. Hệ thống Touch Events (touchEvent.h/.cpp)

- **TouchState_t**: Quản lý trạng thái chạm (isTouched, duration, values)
- **EffectState_t**: Quản lý trạng thái hiệu ứng LED
- **TouchEvent_t**: Cấu trúc event cho FreeRTOS queue
- **TouchEventType_t**: Các loại sự kiện chạm (START, END, SHORT, LONG)

#### Các chức năng chính:

- `initTouchSystem()`: Khởi tạo hệ thống touch với FreeRTOS tasks
- `processTouchData(status, value)`: Xử lý dữ liệu từ PIC
- `handleTouchEvent()`: Xử lý logic touch events
- `sendDebugOSCString()`: Gửi debug messages qua OSC
- `sendResolumeEnableOSC()`, `sendResolumeInitOSC()`, etc.: Điều khiển Resolume

### 3. Tasks phân tán (FreeRTOS)

- **touchProcessingTask** (Core 0): Xử lý touch events
- **effectUpdateTask** (Core 1): Cập nhật hiệu ứng rainbow
- **uartTask** (Core 1): Nhận dữ liệu từ PIC, parse touch data
- **udpTask** (Core 0): Xử lý UDP commands
- **wifiTask** (Core 0): Quản lý kết nối WiFi

### 4. Touch Event Flow

```
PIC UART → uartTask → processTouchData() → TouchEvent Queue → touchProcessingTask → OSC/Resolume
```

### 5. UDP Commands được mở rộng

Ngoài các lệnh cũ, thêm:

```json
{"cmd": "CONFIG", "state": 1}  // Bật/tắt config mode
{"cmd": "LEDCTRL", "index": "ALL", "r": 255, "g": 0, "b": 0}  // Điều khiển LED trực tiếp
{"cmd": "RAINBOW", "action": "START"}  // Bắt đầu hiệu ứng rainbow
{"cmd": "LED", "state": 1}  // Bật/tắt LED system
{"cmd": "DIR", "direction": 1}  // Đặt hướng LED (1=normal, 0=reverse)
{"cmd": "THRESHOLD", "value": 5000}  // Đặt ngưỡng cảm biến touch
```

### 6. OSC Targets

- **Laptop**: 192.168.0.159:7000 (Debug messages)
- **Resolume**: 192.168.0.241:7000 (Control commands)

### 7. Touch Logic

- **Touch Start**: Gửi EnableOSC → Kích hoạt layers trong Resolume
- **Short Touch** (<2s): BackOSC → InitOSC (sau delay)
- **Long Touch** (≥2s): MainOSC → Rainbow Effect → InitOSC

### 8. Hiệu ứng LED

- **Rainbow Caterpillar**: Hiệu ứng chính khi long touch
- **Touch Response**: LED thay đổi theo trạng thái touch
- **Direction Control**: LED có thể chạy thuận/nghịch
- **Brightness Control**: Điều chỉnh độ sáng qua UDP

### 9. Debug và Monitoring

- OSC debug messages gửi về laptop
- Serial output với mutex protection
- WiFi status monitoring
- Touch data logging

## Cách sử dụng

1. **Build và Upload**:

```bash
platformio run --target upload
```

2. **Monitor Serial**:

```bash
platformio device monitor
```

3. **Kiểm tra UDP**:

- Send JSON commands đến ESP32 IP:7000
- Nhận debug messages từ ESP32 tại laptop:7000

4. **Touch Testing**:

- Chạm ngắn: Activate → Back → Init sequence
- Chạm dài: Activate → Main effect → Rainbow → Init

## Lợi ích của cấu trúc mới

1. **Performance**: FreeRTOS tasks chạy parallel
2. **Reliability**: Better error handling, retry mechanisms
3. **Scalability**: Dễ thêm features mới
4. **Debugging**: Comprehensive logging và OSC debug
5. **Platform Compatibility**: Sử dụng thư viện PlatformIO chính thức
6. **Code Organization**: Tách biệt các chức năng rõ ràng

## Cấu hình mạng

- **SSID**: "Cube Touch"
- **Password**: "admin123"
- **ESP32 IP**: 192.168.0.43 (static)
- **Gateway**: 192.168.0.1
- **Subnet**: 255.255.255.0
