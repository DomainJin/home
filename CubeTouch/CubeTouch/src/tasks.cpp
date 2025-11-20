#include "main.h"
#include "led.h"
#include "udpLed.h"
#include "touchEvent.h"

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
    
    // Test network connectivity by sending a ping packet
    if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
        Serial.println("Sending startup notification to laptop...");
        xSemaphoreGive(serialMutex);
    }
    
    // Send startup notification
    udp.beginPacket(laptop_IP, udpMonitorPort);
    udp.print("{\"status\":\"ESP32_READY\",\"ip\":\"" + WiFi.localIP().toString() + "\"}");
    udp.endPacket();
    
    // Send initial OSC debug message
    vTaskDelay(pdMS_TO_TICKS(2000)); // Wait for network to settle
    String startMsg = "ESP32 with Touch System Ready - PlatformIO Build";
    sendDebugOSCString(startMsg);
    
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
    // Wait for WiFi to be connected before starting UDP operations
    while (WiFi.status() != WL_CONNECTED) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
    
    if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
        Serial.println("UDP Task started - listening for packets");
        xSemaphoreGive(serialMutex);
    }
    
    // Variables for UDP processing (from main1.ino)
    char incomingPacket[255];
    extern bool touchProcessingDisabled;
    extern bool configMode;
    
    while (1) {
        // Check for UDP packets (same as main1.ino)
        int packetSize = udp.parsePacket();
        if (packetSize) {
            int len = udp.read(incomingPacket, 254);
            incomingPacket[len] = 0;
            
            if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                Serial.printf("Received: %s\n", incomingPacket);
                xSemaphoreGive(serialMutex);
            }
            
            // Config mode commands (from main1.ino)
            if (strncmp(incomingPacket, "CONFIG:", 7) == 0) {
                int configState = atoi(incomingPacket + 7);
                configMode = (configState == 1);
                if (configMode) {
                    touchProcessingDisabled = true;
                    effectState.effectEnable = true;
                } else {
                    touchProcessingDisabled = false;
                }
                if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                    Serial.printf("Config Mode: %s\n", configMode ? "ON" : "OFF");
                    xSemaphoreGive(serialMutex);
                }
            }
            
            // LED control commands (config mode only)
            else if (strncmp(incomingPacket, "LEDCTRL:", 8) == 0 && configMode) {
                String command = String(incomingPacket + 8);
                int firstComma = command.indexOf(',');
                int secondComma = command.indexOf(',', firstComma + 1);
                int thirdComma = command.indexOf(',', secondComma + 1);
                
                if (firstComma > 0 && secondComma > 0 && thirdComma > 0) {
                    String indexStr = command.substring(0, firstComma);
                    int r = command.substring(firstComma + 1, secondComma).toInt();
                    int g = command.substring(secondComma + 1, thirdComma).toInt();
                    int b = command.substring(thirdComma + 1).toInt();
                    
                    if (indexStr == "ALL") {
                        for (int i = 0; i < LED_COUNT; i++) {
                            strip.setPixelColor(i, strip.Color(r, g, b));
                        }
                    } else {
                        int index = indexStr.toInt();
                        if (index >= 0 && index < LED_COUNT) {
                            strip.setPixelColor(index, strip.Color(r, g, b));
                        }
                    }
                    strip.show();
                    if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                        Serial.printf("Direct LED Control: %s R=%d G=%d B=%d\n", indexStr.c_str(), r, g, b);
                        xSemaphoreGive(serialMutex);
                    }
                }
            }
            
            // Rainbow effect (config mode only)
            else if (strcmp(incomingPacket, "RAINBOW:START") == 0 && configMode) {
                startRainbowEffect();
                if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                    Serial.println("Rainbow effect started via config mode");
                    xSemaphoreGive(serialMutex);
                }
            }
            
            // LED enable/disable
            else if (strncmp(incomingPacket, "LED:", 4) == 0) {
                int ledState = atoi(incomingPacket + 4);
                effectState.effectEnable = (ledState == 1);
                if (!effectState.effectEnable) {
                    for (int i = 0; i < LED_COUNT; i++) {
                        strip.setPixelColor(i, strip.Color(0, 0, 0));
                    }
                    strip.show();
                }
                if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                    Serial.printf("LED Control: %s\n", effectState.effectEnable ? "ON" : "OFF");
                    xSemaphoreGive(serialMutex);
                }
            }
            
            // Threshold setting
            else if (strncmp(incomingPacket, "THRESHOLD:", 10) == 0) {
                int thresholdValue = atoi(incomingPacket + 10);
                extern HardwareSerial SerialPIC;
                SerialPIC.print("THRESHOLD:");
                SerialPIC.print(thresholdValue);
                SerialPIC.print("\n");
                if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                    Serial.printf("Sent threshold to PIC: %d\n", thresholdValue);
                    xSemaphoreGive(serialMutex);
                }
            }
            
            // Brightness control  
            else if (strcmp(incomingPacket, "UP") == 0) {
                int brightness = strip.getBrightness() + 16;
                if (brightness > 255) brightness = 255;
                strip.setBrightness(brightness);
                if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                    Serial.printf("Brightness UP: %d\n", brightness);
                    xSemaphoreGive(serialMutex);
                }
            }
            else if (strcmp(incomingPacket, "DOWN") == 0) {
                int brightness = strip.getBrightness() - 16;
                if (brightness < 1) brightness = 1;
                strip.setBrightness(brightness);
                if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                    Serial.printf("Brightness DOWN: %d\n", brightness);
                    xSemaphoreGive(serialMutex);
                }
            }
            
            // Color setting (RGB format)
            else {
                int r, g, b;
                if (sscanf(incomingPacket, "%d %d %d", &r, &g, &b) == 3) {
                    currentRed = r; 
                    currentGreen = g; 
                    currentBlue = b;
                    if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                        Serial.printf("Set color: R=%d G=%d B=%d\n", r, g, b);
                        xSemaphoreGive(serialMutex);
                    }
                }
            }
        }
        
        // Shorter delay for more responsive UDP handling
        vTaskDelay(pdMS_TO_TICKS(10));
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