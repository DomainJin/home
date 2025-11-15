# CubeTouch - ESP32 LED Controller

ESP32-based LED controller with WiFi and UART communication for LilyGO T-Display board.

## Features

- **WiFi UDP Communication**: Control LEDs from laptop via WiFi
- **UART Communication**: Receive data from PIC microcontroller
- **WS2812 LED Control**: Control 100 addressable LEDs
- **Multiple LED Effects**: Rainbow, Running Light, Breathing, Solid Color
- **Real-time Data Forwarding**: Forward PIC data to laptop via WiFi

## Hardware

- **Board**: LilyGO T-Display (ESP32)
- **LED Strip**: WS2812 (100 LEDs) connected to pin 5
- **UART**: PIC communication (TX: pin 33, RX: pin 26, 9600 baud)
- **WiFi**: Static IP 192.168.0.43

## Software Architecture

```
src/
├── main.cpp          # Main program
├── led.cpp           # LED effects and control
├── udpLed.cpp        # WiFi UDP communication
└── uartPic.cpp       # UART communication with PIC

include/
├── main.h            # Global definitions
├── led.h             # LED function declarations
├── udpLed.h          # UDP function declarations
└── uartPic.h         # UART function declarations
```

## WiFi Configuration

- **SSID**: "Cube Touch"
- **Password**: "admin123"
- **ESP32 IP**: 192.168.0.43
- **Laptop IP**: 192.168.0.159
- **UDP Port**: 7000

## LED Effects

1. **Solid Color** (0): Static color display
2. **Rainbow** (1): Moving rainbow pattern
3. **Running Light** (2): Chasing light effect
4. **Breathing** (3): Pulsing brightness effect

## UDP Commands (JSON Format)

### Set Color
```json
{"cmd": "setColor", "r": 255, "g": 0, "b": 0}
```

### Set Effect
```json
{"cmd": "setEffect", "effect": 1}
```

### Set Brightness
```json
{"cmd": "setBrightness", "brightness": 128}
```

### Turn Off
```json
{"cmd": "off"}
```

### Get Status
```json
{"cmd": "status"}
```

## UART Data Flow

```
PIC → UART (9600 baud) → ESP32 → WiFi UDP → Laptop
```

- ESP32 receives data from PIC via UART
- Automatically forwards to laptop with format: `PIC:data`
- Real-time monitoring via Python GUI

## Python Controller

Run the laptop controller GUI:

```bash
python laptop_controller.py
```

Features:
- Color picker and RGB sliders
- Effect selection buttons
- Brightness control
- Real-time PIC data display
- Status monitoring

## Installation

### PlatformIO
```bash
pio run --target upload
pio device monitor
```

### Dependencies
- Adafruit NeoPixel
- ArduinoJson
- WiFi (built-in)

### Python Requirements
```bash
pip install tkinter
```

## Pin Connections

| Function | ESP32 Pin |
|----------|-----------|
| LED Data | 5         |
| UART TX  | 33        |
| UART RX  | 26        |

## Usage

1. Connect hardware according to pin diagram
2. Update WiFi credentials if needed
3. Upload firmware to ESP32
4. Run Python controller on laptop
5. Monitor PIC data and control LEDs

## License

MIT License - Feel free to use and modify for your projects.

## Author

Created for IoT LED control and PIC communication projects.