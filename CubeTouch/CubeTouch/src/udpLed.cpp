#include "udpLed.h"
#include "led.h"
#include "uart.h"

void initUDP() {
    udp.begin(udpPort);
    if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
        Serial.printf("UDP server started on port %d\n", udpPort);
        xSemaphoreGive(serialMutex);
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
    else if (command == "status") {
        sendStatus();
    }
}

void sendResponse(String message) {
    udp.beginPacket(laptop_IP, udpPort);
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