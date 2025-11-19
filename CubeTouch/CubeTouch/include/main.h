#ifndef MAIN_H
#define MAIN_H

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <freertos/queue.h>
#include <freertos/semphr.h>

// Pin definitions
#define LED_PIN    5
#define LED_COUNT  100

// UART 
#define UART_TX_PIN 26  // TX pin 
#define UART_RX_PIN 33  // RX pin 
#define UART_BAUD 9600

// Task priorities
#define UART_TASK_PRIORITY      2
#define LED_TASK_PRIORITY       1
#define UDP_TASK_PRIORITY       2
#define WIFI_TASK_PRIORITY      3

// Stack sizes
#define UART_TASK_STACK_SIZE    4096
#define LED_TASK_STACK_SIZE     4096
#define UDP_TASK_STACK_SIZE     4096
#define WIFI_TASK_STACK_SIZE    4096

// Event types
typedef enum {
    EVENT_UART_DATA,
    EVENT_UDP_COMMAND,
    EVENT_LED_UPDATE,
    EVENT_WIFI_STATUS
} EventType_t;

// Event structure
typedef struct {
    EventType_t type;
    String data;
    uint8_t r, g, b;
    int effect;
    bool autoMode;
} CustomEvent_t;

// WiFi settings
extern const char* ssid;
extern const char* password;
extern IPAddress local_IP;
extern IPAddress gateway;
extern IPAddress subnet;
extern IPAddress laptop_IP;
extern const unsigned int udpMonitorPort;

// Global objects
extern WiFiUDP udp;
extern Adafruit_NeoPixel strip;
extern HardwareSerial uartSerial;

// LED control variables
extern uint8_t currentRed, currentGreen, currentBlue;
extern int currentEffect;
extern bool autoMode;

// FreeRTOS objects
extern QueueHandle_t eventQueue;
extern SemaphoreHandle_t serialMutex;
extern TaskHandle_t uartTaskHandle;
extern TaskHandle_t ledTaskHandle;
extern TaskHandle_t udpTaskHandle;
extern TaskHandle_t wifiTaskHandle;

// Task functions
void uartTask(void *parameter);
void ledTask(void *parameter);
void udpTask(void *parameter);
void wifiTask(void *parameter);
void eventProcessorTask(void *parameter);

#endif