#include "udpLed.h"
#include "led.h"
#include "uart.h"
#include "touchEvent.h"

void initUDP() {
    if (udp.begin(udpMonitorPort)) {
        if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            Serial.printf("UDP server started successfully on port %d\n", udpMonitorPort);
            Serial.printf("ESP32 IP: %s\n", WiFi.localIP().toString().c_str());
            Serial.printf("Laptop IP: %s\n", laptop_IP.toString().c_str());
            xSemaphoreGive(serialMutex);
        }
    } else {
        if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            Serial.printf("FAILED to start UDP server on port %d\n", udpMonitorPort);
            xSemaphoreGive(serialMutex);
        }
    }
}

void handleUDP() {
    // This function is now handled by udpTask in tasks.cpp
    // Keeping for compatibility
}

void processCommand(JsonDocument& doc) {
    String command = doc["cmd"];
    
    CustomEvent_t event;
    event.type = EVENT_LED_UPDATE;
    
    if (command == "setColor") {
        event.r = doc["r"];
        event.g = doc["g"];
        event.b = doc["b"];
        event.autoMode = false;
        
        xQueueSend(eventQueue, &event, pdMS_TO_TICKS(100));
        
        if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            Serial.printf("Set color: R=%d, G=%d, B=%d\n", event.r, event.g, event.b);
            xSemaphoreGive(serialMutex);
        }
    }
    else if (command == "setEffect") {
        event.effect = doc["effect"];
        event.autoMode = true;
        
        xQueueSend(eventQueue, &event, pdMS_TO_TICKS(100));
        
        if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            Serial.printf("Set effect: %d\n", event.effect);
            xSemaphoreGive(serialMutex);
        }
    }
    else if (command == "setBrightness") {
        int brightness = doc["brightness"];
        strip.setBrightness(brightness);
        strip.show();
        if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            Serial.printf("Set brightness: %d\n", brightness);
            xSemaphoreGive(serialMutex);
        }
    }
    else if (command == "off") {
        event.r = 0;
        event.g = 0;
        event.b = 0;
        event.autoMode = false;
        
        xQueueSend(eventQueue, &event, pdMS_TO_TICKS(100));
        
        if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            Serial.println("LEDs turned off");
            xSemaphoreGive(serialMutex);
        }
    }
    // ===== NEW COMMANDS FROM MAIN1.INO =====
    else if (command == "CONFIG") {
        int configState = doc["state"];
        bool configMode = (configState == 1);
        
        // Store config mode state (you might want to add this to global variables)
        extern bool touchProcessingDisabled;
        touchProcessingDisabled = configMode ? true : false;
        
        if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            Serial.printf("Config Mode: %s\n", configMode ? "ON" : "OFF");
            xSemaphoreGive(serialMutex);
        }
    }
    else if (command == "LEDCTRL") {
        // Direct LED control for config mode
        String index = doc["index"];
        int r = doc["r"];
        int g = doc["g"];
        int b = doc["b"];
        
        if (index == "ALL") {
            for (int i = 0; i < LED_COUNT; i++) {
                strip.setPixelColor(i, strip.Color(r, g, b));
            }
        } else {
            int ledIndex = index.toInt();
            if (ledIndex >= 0 && ledIndex < LED_COUNT) {
                strip.setPixelColor(ledIndex, strip.Color(r, g, b));
            }
        }
        strip.show();
        
        if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            Serial.printf("Direct LED Control: %s R=%d G=%d B=%d\n", index.c_str(), r, g, b);
            xSemaphoreGive(serialMutex);
        }
    }
    else if (command == "RAINBOW") {
        String action = doc["action"];
        if (action == "START") {
            startRainbowEffect();
            if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                Serial.println("Rainbow effect started via UDP");
                xSemaphoreGive(serialMutex);
            }
        }
    }
    else if (command == "LED") {
        int ledState = doc["state"];
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
    else if (command == "DIR") {
        int direction = doc["direction"];
        effectState.ledDirection = (direction == 1) ? 1 : 0;
        if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            Serial.printf("LED Direction: %d\n", effectState.ledDirection);
            xSemaphoreGive(serialMutex);
        }
    }
    else if (command == "THRESHOLD") {
        int thresholdValue = doc["value"];
        // Send threshold to PIC via UART
        String thresholdCmd = "THRESHOLD:" + String(thresholdValue);
        uartSerial.println(thresholdCmd);
        if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            Serial.printf("Sent threshold to PIC: %d\n", thresholdValue);
            xSemaphoreGive(serialMutex);
        }
    }
    else if (command == "status") {
        sendStatus();
    }
}

void sendResponse(String message) {
    udp.beginPacket(laptop_IP, udpMonitorPort);
    udp.print(message);
    udp.endPacket();
}

void sendStatus() {
    JsonDocument doc;
    doc["ip"] = WiFi.localIP().toString();
    doc["effect"] = currentEffect;
    doc["auto"] = autoMode;
    doc["r"] = currentRed;
    doc["g"] = currentGreen;
    doc["b"] = currentBlue;
    doc["brightness"] = strip.getBrightness();
    
    String response;
    serializeJson(doc, response);
    sendResponse(response);
}