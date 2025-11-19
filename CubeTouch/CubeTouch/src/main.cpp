#include "main.h"
#include "led.h"
#include "udpLed.h"
#include "uart.h"

// WiFi settings
const char* ssid = "Cube Touch";
const char* password = "admin123";

// Static IP configuration
IPAddress local_IP(192, 168, 0, 43);
IPAddress gateway(192, 168, 0, 1);
IPAddress subnet(255, 255, 255, 0);

// Laptop IP and UDP port
IPAddress laptop_IP(192, 168, 0, 159);
const unsigned int udpMonitorPort = 7000;

WiFiUDP udp;
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);
HardwareSerial uartSerial(2); // Use UART2 for normal serial communication

// LED control variables
uint8_t currentRed = 255, currentGreen = 0, currentBlue = 0;
int currentEffect = 0; // 0: solid, 1: rainbow, 2: running, 3: breathing
bool autoMode = true;

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
    Serial.println("ESP32 starting with FreeRTOS tasks...");
    
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