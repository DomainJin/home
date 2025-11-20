#include "main.h"
#include "led.h"
#include "udpLed.h"
#include "uart.h"
#include "touchEvent.h"
#include "config.h"

// WiFi settings
const char* ssid = WIFI_SSID;
const char* password = WIFI_PASSWORD;

// Static IP configuration
IPAddress local_IP(ESP32_IP_ADDR);
IPAddress gateway(GATEWAY_IP_ADDR);
IPAddress subnet(SUBNET_MASK);

// Laptop IP and UDP port
IPAddress laptop_IP(LAPTOP_IP_ADDR);
const unsigned int udpMonitorPort = UDP_MONITOR_PORT;

WiFiUDP udp;
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);
HardwareSerial uartSerial(2); // Use UART2 for normal serial communication

// LED control variables
uint8_t currentRed = DEFAULT_RED, currentGreen = DEFAULT_GREEN, currentBlue = DEFAULT_BLUE;
int currentEffect = 0; // 0: solid, 1: rainbow, 2: running, 3: breathing
bool autoMode = true;

// Touch control variables
bool touchProcessingDisabled = false;
bool configMode = false;

// UART processing variables (from main1.ino)
String uartBuffer = "";
String uartLabel = "";
int latestStatus = -1;
int latestValue = -1;

// SerialPIC for communication with PIC (like main1.ino)
HardwareSerial SerialPIC(1);

// FreeRTOS objects
QueueHandle_t eventQueue;
SemaphoreHandle_t serialMutex;
TaskHandle_t uartTaskHandle;
TaskHandle_t ledTaskHandle;
TaskHandle_t udpTaskHandle;
TaskHandle_t wifiTaskHandle;
TaskHandle_t eventProcessorTaskHandle;

void setup() {
    Serial.begin(115200);
    SerialPIC.begin(9600, SERIAL_8N1, 33, 26);  // Initialize SerialPIC like main1.ino
    Serial.println("ESP32 starting with FreeRTOS tasks...");
    Serial.println("ESP32 Ready to receive from PIC!");
    
    // Create mutex for serial access
    serialMutex = xSemaphoreCreateMutex();
    
    // Create event queue
    eventQueue = xQueueCreate(10, sizeof(CustomEvent_t));
    
    if (eventQueue == NULL || serialMutex == NULL) {
        Serial.println("Failed to create FreeRTOS objects!");
        return;
    }
    
    // Initialize hardware
    initLEDs();
    initUART();
    initTouchSystem();
    
    // Test OSC debug message
    String startMsg = "ESP32 Started with Touch System - PlatformIO Build";
    sendDebugOSCString(startMsg);
    
    // Create tasks
    xTaskCreatePinnedToCore(
        wifiTask,
        "WiFi Task",
        WIFI_TASK_STACK_SIZE,
        NULL,
        WIFI_TASK_PRIORITY,
        &wifiTaskHandle,
        0  // Core 0
    );
    
    xTaskCreatePinnedToCore(
        uartTask,
        "UART Task",
        UART_TASK_STACK_SIZE,
        NULL,
        UART_TASK_PRIORITY,
        &uartTaskHandle,
        1  // Core 1
    );
    
    xTaskCreatePinnedToCore(
        ledTask,
        "LED Task",
        LED_TASK_STACK_SIZE,
        NULL,
        LED_TASK_PRIORITY,
        &ledTaskHandle,
        1  // Core 1
    );
    
    xTaskCreatePinnedToCore(
        udpTask,
        "UDP Task",
        UDP_TASK_STACK_SIZE,
        NULL,
        UDP_TASK_PRIORITY,
        &udpTaskHandle,
        0  // Core 0
    );
    
    xTaskCreatePinnedToCore(
        eventProcessorTask,
        "Event Processor",
        4096,
        NULL,
        3,
        &eventProcessorTaskHandle,
        0  // Core 0
    );
    
    Serial.println("All tasks created successfully!");
}

void loop() {
    // Empty - everything runs in tasks
    vTaskDelay(pdMS_TO_TICKS(1000));
}