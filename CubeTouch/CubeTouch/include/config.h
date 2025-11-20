#ifndef CONFIG_H
#define CONFIG_H

// ===== NETWORK CONFIGURATION =====
#define WIFI_SSID "Cube Touch"
#define WIFI_PASSWORD "admin123"

// Static IP configuration
#define ESP32_IP_ADDR 192,168,0,43
#define GATEWAY_IP_ADDR 192,168,0,1
#define SUBNET_MASK 255,255,255,0

// Target IPs
#define LAPTOP_IP_ADDR 192,168,0,159
#define RESOLUME_IP_ADDR 192,168,0,241

// Port configuration
#define UDP_MONITOR_PORT 7000
#define OSC_RESOLUME_PORT 7000
#define OSC_LAPTOP_PORT 7000
#define UDP_LOCAL_PORT 4210

// ===== HARDWARE CONFIGURATION =====
#define LED_PIN 5
#define LED_COUNT 150  // Update to match main1.ino
#define UART_TX_PIN 26
#define UART_RX_PIN 33
#define UART_BAUD 9600

// ===== TOUCH SYSTEM CONFIGURATION =====
#define MAIN_EFFECT_TIME 6000    // Main effect duration (ms)
#define OPERATION_TIME 2000      // Short vs long touch threshold (ms)
#define OSC_INTERVAL 100         // OSC throttling interval (ms)
#define UPDATE_INTERVAL 5        // LED update interval (ms)
#define TOUCH_THRESHOLD 5147     // Default touch threshold

// ===== LED CONFIGURATION =====
#define DEFAULT_BRIGHTNESS 255
#define DEFAULT_RED 43
#define DEFAULT_GREEN 159
#define DEFAULT_BLUE 2

// ===== FREERTOS CONFIGURATION =====
#define UART_TASK_PRIORITY 2
#define LED_TASK_PRIORITY 1
#define UDP_TASK_PRIORITY 2
#define WIFI_TASK_PRIORITY 3
#define TOUCH_TASK_PRIORITY 2
#define EFFECT_TASK_PRIORITY 1

#define UART_TASK_STACK_SIZE 4096
#define LED_TASK_STACK_SIZE 4096
#define UDP_TASK_STACK_SIZE 4096
#define WIFI_TASK_STACK_SIZE 4096
#define TOUCH_TASK_STACK_SIZE 4096
#define EFFECT_TASK_STACK_SIZE 4096

#define EVENT_QUEUE_SIZE 10
#define TOUCH_QUEUE_SIZE 10

// ===== DEBUG CONFIGURATION =====
#define ENABLE_SERIAL_DEBUG 1
#define ENABLE_OSC_DEBUG 1
#define ENABLE_WIFI_DEBUG 1
#define ENABLE_TOUCH_DEBUG 1

// Serial debug macros
#if ENABLE_SERIAL_DEBUG
    #define DEBUG_PRINT(x) Serial.print(x)
    #define DEBUG_PRINTLN(x) Serial.println(x)
    #define DEBUG_PRINTF(...) Serial.printf(__VA_ARGS__)
#else
    #define DEBUG_PRINT(x)
    #define DEBUG_PRINTLN(x)
    #define DEBUG_PRINTF(...)
#endif

// OSC debug control
#if ENABLE_OSC_DEBUG
    #define OSC_DEBUG_ENABLED true
#else
    #define OSC_DEBUG_ENABLED false
#endif

#endif