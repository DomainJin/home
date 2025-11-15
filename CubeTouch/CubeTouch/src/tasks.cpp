#include "main.h"
#include "led.h"
#include "udpLed.h"

// WiFi Task - runs on Core 0
void wifiTask(void *parameter) {
    // Configure static IP
    if (!WiFi.config(local_IP, gateway, subnet)) {
        if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            Serial.println("Failed to configure static IP");
            xSemaphoreGive(serialMutex);
        }
    }
    
    // Connect to WiFi
    WiFi.begin(ssid, password);
    
    if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
        Serial.print("Connecting to WiFi");
        xSemaphoreGive(serialMutex);
    }
    
    while (WiFi.status() != WL_CONNECTED) {
        vTaskDelay(pdMS_TO_TICKS(500));
        if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            Serial.print(".");
            xSemaphoreGive(serialMutex);
        }
    }
    
    if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
        Serial.println();
        Serial.println("WiFi connected!");
        Serial.print("ESP32 IP: ");
        Serial.println(WiFi.localIP());
        xSemaphoreGive(serialMutex);
    }
    
    // Start UDP
    initUDP();
    
    // Monitor WiFi status
    while (1) {
        if (WiFi.status() != WL_CONNECTED) {
            CustomEvent_t event;
            event.type = EVENT_WIFI_STATUS;
            event.data = "disconnected";
            xQueueSend(eventQueue, &event, 0);
            
            // Try to reconnect
            WiFi.reconnect();
        }
        
        vTaskDelay(pdMS_TO_TICKS(5000)); // Check every 5 seconds
    }
}

// UDP Task - runs on Core 0
void udpTask(void *parameter) {
    while (1) {
        // Only check for packets if UDP is properly initialized
        if (udp.available()) {
            int packetSize = udp.parsePacket();
            if (packetSize > 0) {
                char incomingPacket[255];
                int len = udp.read(incomingPacket, packetSize);
                if (len > 0) {
                    incomingPacket[len] = 0;
                    
                    if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                        Serial.printf("Received from laptop: %s\n", incomingPacket);
                        xSemaphoreGive(serialMutex);
                    }
                    
                    // Parse JSON command
                    JsonDocument doc;
                    DeserializationError error = deserializeJson(doc, incomingPacket);
                    
                    if (!error) {
                        CustomEvent_t event;
                        event.type = EVENT_UDP_COMMAND;
                        event.data = String(incomingPacket);
                        xQueueSend(eventQueue, &event, pdMS_TO_TICKS(100));
                    } else {
                        if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                            Serial.println("Failed to parse JSON");
                            xSemaphoreGive(serialMutex);
                        }
                        sendResponse("ERROR: Invalid JSON");
                    }
                }
            }
        }
        
        // Longer delay to reduce UDP polling frequency
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}

// LED Task - runs on Core 1
void ledTask(void *parameter) {
    TickType_t lastWakeTime = xTaskGetTickCount();
    const TickType_t frequency = pdMS_TO_TICKS(50); // 50ms for smooth effects
    
    while (1) {
        if (autoMode) {
            runLEDEffect();
        }
        
        vTaskDelayUntil(&lastWakeTime, frequency);
    }
}

// Event Processor Task - runs on Core 0
void eventProcessorTask(void *parameter) {
    CustomEvent_t event;
    static int touchValue = 0;
    static int threshold = 0;
    static bool touchDetected = false;
    
    while (1) {
        if (xQueueReceive(eventQueue, &event, pdMS_TO_TICKS(100)) == pdTRUE) {
            switch (event.type) {
                case EVENT_UART_DATA:
                    if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                        // Serial.printf("PIC Data: %s\n", event.data.c_str());
                        xSemaphoreGive(serialMutex);
                    }
                    
                    // Parse touch data from PIC
                    if (event.data.indexOf("value") >= 0) {
                        // Next data will be touch value
                    } else if (event.data.toInt() > 0 && event.data.length() == 4) {
                        // This is a numeric value (touch reading or threshold)
                        int value = event.data.toInt();
                        if (value > 4000) { // Likely a touch value
                            touchValue = value;
                        }
                    } else if (event.data.indexOf("Threshold") >= 0) {
                        // Next data will be threshold
                    } else if (event.data.indexOf("RawTouch") >= 0) {
                        // Next data will be raw touch (0 or 1)
                    } else if (event.data == "0" || event.data == "1") {
                        // Touch detection result
                        bool newTouchState = (event.data == "1");
                        if (newTouchState != touchDetected) {
                            touchDetected = newTouchState;
                            
                            // Create LED event based on touch
                            CustomEvent_t ledEvent;
                            ledEvent.type = EVENT_LED_UPDATE;
                            if (touchDetected) {
                                ledEvent.r = 0;
                                ledEvent.g = 255;
                                ledEvent.b = 0;  // Green when touched
                            } else {
                                ledEvent.r = 255;
                                ledEvent.g = 0;
                                ledEvent.b = 0;  // Red when not touched
                            }
                            ledEvent.autoMode = false;
                            
                            xQueueSend(eventQueue, &ledEvent, 0);
                            
                            if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                                Serial.printf("Touch %s - Value: %d\n", 
                                    touchDetected ? "DETECTED" : "RELEASED", touchValue);
                                xSemaphoreGive(serialMutex);
                            }
                        }
                    }
                    break;
                    
                case EVENT_UDP_COMMAND:
                    {
                        JsonDocument doc;
                        DeserializationError error = deserializeJson(doc, event.data);
                        if (!error) {
                            processCommand(doc);
                            sendResponse("OK");
                        }
                    }
                    break;
                    
                case EVENT_LED_UPDATE:
                    currentRed = event.r;
                    currentGreen = event.g;
                    currentBlue = event.b;
                    currentEffect = event.effect;
                    autoMode = event.autoMode;
                    
                    if (!autoMode) {
                        setAllLEDs(currentRed, currentGreen, currentBlue);
                    }
                    break;
                    
                case EVENT_WIFI_STATUS:
                    if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                        Serial.printf("WiFi Status: %s\n", event.data.c_str());
                        xSemaphoreGive(serialMutex);
                    }
                    break;
                    
                default:
                    break;
            }
        }
    }
}