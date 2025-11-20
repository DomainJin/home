#include "touchEvent.h"
#include "led.h"
#include "config.h"

// OSC targets - IP addresses for Resolume and laptop
const IPAddress resolume_ip(RESOLUME_IP_ADDR);
const unsigned int resolume_port = OSC_RESOLUME_PORT;
const unsigned int laptop_port = OSC_LAPTOP_PORT;

// Global state variables
TouchState_t touchState = {
    .isTouched = false,
    .sentOSCOnce = false,
    .touchStartMillis = 0,
    .lastTouchDuration = 0,
    .latestStatus = -1,
    .latestValue = -1,
    .lastOSCTime = 0,
    .lastSentStatus = -2,
    .lastSentValue = -2
};

EffectState_t effectState = {
    .waitingMainEffect = false,
    .waitInitAfterBack = false,
    .mainEffectStartMillis = 0,
    .timeCountdownInit = 0,
    .mainEffectStarted = false,
    .effectEnable = true,
    .ledDirection = 1,
    .rainbowEffectActive = false,
    .rainbowStartTime = 0,
    .rainbowOffset = 0
};

// FreeRTOS objects for touch system
QueueHandle_t touchEventQueue;
TaskHandle_t touchProcessingTaskHandle;
TaskHandle_t effectUpdateTaskHandle;

void initTouchSystem() {
    // Create touch event queue
    touchEventQueue = xQueueCreate(10, sizeof(TouchEvent_t));
    
    if (touchEventQueue == NULL) {
        if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            Serial.println("Failed to create touch event queue!");
            xSemaphoreGive(serialMutex);
        }
        return;
    }
    
    // Create touch processing task
    xTaskCreatePinnedToCore(
        touchProcessingTask,
        "Touch Processing",
        4096,
        NULL,
        2,
        &touchProcessingTaskHandle,
        0  // Core 0
    );
    
    // Create effect update task
    xTaskCreatePinnedToCore(
        effectUpdateTask,
        "Effect Update",
        4096,
        NULL,
        1,
        &effectUpdateTaskHandle,
        1  // Core 1
    );
    
    if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
        Serial.println("Touch system initialized successfully");
        xSemaphoreGive(serialMutex);
    }
}

void processTouchData(int status, int value) {
    // Update latest values
    touchState.latestStatus = status;
    touchState.latestValue = value;
    
    // Create touch event
    TouchEvent_t event;
    event.value = value;
    event.status = status;
    event.timestamp = millis();
    
    // Determine event type
    if (status == 1 && !touchState.isTouched) {
        event.type = TOUCH_EVENT_START;
        touchState.isTouched = true;
        touchState.touchStartMillis = event.timestamp;
        touchState.sentOSCOnce = false;
    } else if (status == 0 && touchState.isTouched) {
        event.type = TOUCH_EVENT_END;
        event.duration = event.timestamp - touchState.touchStartMillis;
        touchState.lastTouchDuration = event.duration;
        touchState.isTouched = false;
        touchState.sentOSCOnce = false;
        
        // Determine if short or long touch
        if (event.duration < OPERATION_TIME && event.duration > 0) {
            event.type = TOUCH_EVENT_SHORT;
        } else if (event.duration >= OPERATION_TIME) {
            event.type = TOUCH_EVENT_LONG;
        }
    } else {
        event.type = TOUCH_EVENT_NONE;
    }
    
    // Send event to queue
    if (event.type != TOUCH_EVENT_NONE) {
        xQueueSend(touchEventQueue, &event, pdMS_TO_TICKS(10));
    }
}

void sendDebugOSCString(const String& message) {
    // Check WiFi connection first
    if (WiFi.status() != WL_CONNECTED) {
        if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            Serial.println("[ERROR] WiFi disconnected! Cannot send OSC.");
            xSemaphoreGive(serialMutex);
        }
        return;
    }
    
    SimpleOSCMessage msg("/debug");
    msg.add(message.c_str());
    
    // Retry mechanism for OSC sending
    int maxRetries = 3;
    bool sent = false;
    
    for (int retry = 0; retry < maxRetries && !sent; retry++) {
        int result = udp.beginPacket(laptop_IP, laptop_port);
        if (result == 1) {
            msg.send(udp);
            int endResult = udp.endPacket();
            if (endResult == 1) {
                sent = true;
                if (retry > 0 && xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                    Serial.printf("[OSC DEBUG] Packet sent on retry %d\\n", retry + 1);
                    xSemaphoreGive(serialMutex);
                }
            } else {
                if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                    Serial.printf("[OSC ERROR] Failed to end packet (attempt %d)\\n", retry + 1);
                    xSemaphoreGive(serialMutex);
                }
                delay(10);
            }
        } else {
            if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                Serial.printf("[OSC ERROR] Failed to begin packet (attempt %d)\\n", retry + 1);
                xSemaphoreGive(serialMutex);
            }
            delay(10);
        }
    }
    
    if (!sent && xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
        Serial.println("[OSC ERROR] Failed to send after all retries!");
        xSemaphoreGive(serialMutex);
    }
    
    msg.empty();
}

void sendResolumeEnableOSC(int durationMs) {
    if (WiFi.status() != WL_CONNECTED) {
        return;
    }
    
    if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
        Serial.printf("[OSC->Resolume] Sending Enable commands to %s:%d\\n", 
                     resolume_ip.toString().c_str(), resolume_port);
        xSemaphoreGive(serialMutex);
    }
    
    unsigned long startTime = millis();
    while (millis() - startTime < durationMs) {
        // Layer 1
        SimpleOSCMessage msg1("/composition/layers/1/clear");
        msg1.add((int32_t)1);
        SimpleOSCMessage msg2("/composition/layers/1/clips/2/connect");
        msg2.add((int32_t)1);
        SimpleOSCMessage msg3("/composition/layers/1/clips/2/transport/position/behaviour/playdirection");
        msg3.add((int32_t)2);

        // Layer 2
        SimpleOSCMessage msg4("/composition/layers/2/clear");
        msg4.add((int32_t)1);
        SimpleOSCMessage msg5("/composition/layers/2/clips/2/connect");
        msg5.add((int32_t)1);
        SimpleOSCMessage msg6("/composition/layers/2/clips/2/transport/position/behaviour/playdirection");
        msg6.add((int32_t)2);

        // Layer 3
        SimpleOSCMessage msg7("/composition/layers/3/clear");
        msg7.add((int32_t)1);
        SimpleOSCMessage msg8("/composition/layers/3/clips/2/connect");
        msg8.add((int32_t)1);
        SimpleOSCMessage msg9("/composition/layers/3/clips/2/transport/position/behaviour/playdirection");
        msg9.add((int32_t)2);

        // Send all messages to Resolume
        udp.beginPacket(resolume_ip, resolume_port); msg1.send(udp); udp.endPacket(); msg1.empty();
        udp.beginPacket(resolume_ip, resolume_port); msg2.send(udp); udp.endPacket(); msg2.empty();
        udp.beginPacket(resolume_ip, resolume_port); msg3.send(udp); udp.endPacket(); msg3.empty();
        udp.beginPacket(resolume_ip, resolume_port); msg4.send(udp); udp.endPacket(); msg4.empty();
        udp.beginPacket(resolume_ip, resolume_port); msg5.send(udp); udp.endPacket(); msg5.empty();
        udp.beginPacket(resolume_ip, resolume_port); msg6.send(udp); udp.endPacket(); msg6.empty();
        udp.beginPacket(resolume_ip, resolume_port); msg7.send(udp); udp.endPacket(); msg7.empty();
        udp.beginPacket(resolume_ip, resolume_port); msg8.send(udp); udp.endPacket(); msg8.empty();
        udp.beginPacket(resolume_ip, resolume_port); msg9.send(udp); udp.endPacket(); msg9.empty();
    }
}

void sendResolumeInitOSC(int durationMs) {
    unsigned long startTime = millis();
    while (millis() - startTime < durationMs) {
        SimpleOSCMessage msga("/composition/layers/1/clips/1/connect");
        msga.add((int32_t)1);
        SimpleOSCMessage msgs("/composition/layers/1/clips/1/transport/position/behaviour/playdirection");
        msgs.add((int32_t)2);
        
        SimpleOSCMessage msgd("/composition/layers/2/clips/1/connect");
        msgd.add((int32_t)1);
        SimpleOSCMessage msgf("/composition/layers/2/clips/1/transport/position/behaviour/playdirection");
        msgf.add((int32_t)2);
        
        SimpleOSCMessage msgg("/composition/layers/3/clips/1/connect");
        msgg.add((int32_t)1);
        SimpleOSCMessage msgh("/composition/layers/3/clips/1/transport/position/behaviour/playdirection");
        msgh.add((int32_t)2);

        udp.beginPacket(resolume_ip, resolume_port); msga.send(udp); udp.endPacket(); msga.empty();
        udp.beginPacket(resolume_ip, resolume_port); msgs.send(udp); udp.endPacket(); msgs.empty();
        udp.beginPacket(resolume_ip, resolume_port); msgd.send(udp); udp.endPacket(); msgd.empty();
        udp.beginPacket(resolume_ip, resolume_port); msgf.send(udp); udp.endPacket(); msgf.empty();
        udp.beginPacket(resolume_ip, resolume_port); msgg.send(udp); udp.endPacket(); msgg.empty();
        udp.beginPacket(resolume_ip, resolume_port); msgh.send(udp); udp.endPacket(); msgh.empty();
    }
}

void sendResolumeBackOSC(int durationMs) {
    unsigned long startTime = millis();
    while (millis() - startTime < durationMs) {
        SimpleOSCMessage msgq("/composition/layers/1/clips/2/transport/position/behaviour/playdirection");
        msgq.add((int32_t)0);
        SimpleOSCMessage msgw("/composition/layers/2/clips/2/transport/position/behaviour/playdirection");
        msgw.add((int32_t)0);
        
        udp.beginPacket(resolume_ip, resolume_port); msgq.send(udp); udp.endPacket(); msgq.empty();
        udp.beginPacket(resolume_ip, resolume_port); msgw.send(udp); udp.endPacket(); msgw.empty();
    }
}

void sendResolumeMain(int durationMs) {
    unsigned long startTime = millis();
    while (millis() - startTime < durationMs) {
        SimpleOSCMessage msgz("/composition/layers/3/clips/3/connect");
        msgz.add((int32_t)1);
        SimpleOSCMessage msgx("/composition/layers/3/clips/3/transport/position/behaviour/playdirection");
        msgx.add((int32_t)2);

        udp.beginPacket(resolume_ip, resolume_port); msgz.send(udp); udp.endPacket(); msgz.empty();
        udp.beginPacket(resolume_ip, resolume_port); msgx.send(udp); udp.endPacket(); msgx.empty();
    }
}

void handleTouchEvent(TouchEvent_t* event) {
    unsigned long currentTime = millis();
    bool shouldSendOSC = false;
    
    // Check if should send OSC based on throttling and changes
    if (touchState.latestStatus != touchState.lastSentStatus || 
        touchState.latestValue != touchState.lastSentValue) {
        shouldSendOSC = true;
    } else if (currentTime - touchState.lastOSCTime >= OSC_INTERVAL) {
        shouldSendOSC = true;
    }
    
    // Send debug OSC
    if (shouldSendOSC) {
        String debugMsg = "RawTouch: " + String(touchState.latestStatus) + 
                         ", Value: " + String(touchState.latestValue) + 
                         ", Threshold: 5147";
        sendDebugOSCString(debugMsg);
        touchState.lastOSCTime = currentTime;
        touchState.lastSentStatus = touchState.latestStatus;
        touchState.lastSentValue = touchState.latestValue;
    }
    
    // Handle different touch events
    switch (event->type) {
        case TOUCH_EVENT_START:
            if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                Serial.println("[TOUCH] Touch detected!");
                xSemaphoreGive(serialMutex);
            }
            if (!touchState.sentOSCOnce) {
                sendResolumeEnableOSC(5);
                touchState.sentOSCOnce = true;
                if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                    Serial.println("[TOUCH] Sending EnableOSC...");
                    xSemaphoreGive(serialMutex);
                }
            }
            break;
            
        case TOUCH_EVENT_SHORT:
            effectState.timeCountdownInit = millis();
            sendResolumeBackOSC(5);
            effectState.waitInitAfterBack = true;
            if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                Serial.printf("[TOUCH] Touch released (short), duration: %lums\\n", event->duration);
                Serial.println("[TOUCH] Sending BackOSC...");
                xSemaphoreGive(serialMutex);
            }
            break;
            
        case TOUCH_EVENT_LONG:
            sendResolumeMain(5);
            effectState.waitingMainEffect = true;
            effectState.mainEffectStartMillis = millis();
            if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                Serial.printf("[TOUCH] Touch released (long), duration: %lums\\n", event->duration);
                Serial.println("[TOUCH] Triggering main effect...");
                xSemaphoreGive(serialMutex);
            }
            break;
            
        default:
            break;
    }
}

void startRainbowEffect() {
    effectState.rainbowEffectActive = true;
    effectState.rainbowStartTime = millis();
    effectState.rainbowOffset = 0;
    if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
        Serial.println("Rainbow effect started!");
        xSemaphoreGive(serialMutex);
    }
}

void rainbowCaterpillarEffect(unsigned long durationMs) {
    unsigned long startTime = millis();
    int offset = 0;
    
    while (millis() - startTime < durationMs) {
        for (int i = 0; i < LED_COUNT; i++) {
            uint8_t pixelHue = (offset + i * (255 / 7)) % 255;
            uint32_t color = strip.gamma32(strip.ColorHSV(pixelHue * 256));
            strip.setPixelColor(i, color);
        }
        strip.show();
        offset = (offset + 4) % 255;
        vTaskDelay(pdMS_TO_TICKS(UPDATE_INTERVAL));
    }
    
    // Clear all LEDs
    for (int i = 0; i < LED_COUNT; i++) {
        strip.setPixelColor(i, 0);
    }
    strip.show();
}

void updateRainbowEffect() {
    if (!effectState.rainbowEffectActive) return;
    
    unsigned long elapsed = millis() - effectState.rainbowStartTime;
    if (elapsed >= MAIN_EFFECT_TIME) {
        effectState.rainbowEffectActive = false;
        for (int i = 0; i < LED_COUNT; i++) {
            strip.setPixelColor(i, 0);
        }
        strip.show();
        if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            Serial.println("Rainbow effect finished!");
            xSemaphoreGive(serialMutex);
        }
        return;
    }
    
    for (int i = 0; i < LED_COUNT; i++) {
        uint8_t pixelHue = (effectState.rainbowOffset + i * (255 / 7)) % 255;
        uint32_t color = strip.gamma32(strip.ColorHSV(pixelHue * 256));
        strip.setPixelColor(i, color);
    }
    strip.show();
    effectState.rainbowOffset = (effectState.rainbowOffset + 4) % 255;
}

void touchProcessingTask(void *parameter) {
    TouchEvent_t event;
    
    while (true) {
        // Wait for touch events
        if (xQueueReceive(touchEventQueue, &event, pdMS_TO_TICKS(100)) == pdTRUE) {
            handleTouchEvent(&event);
        }
        
        // Check for post-touch effects
        if (effectState.waitInitAfterBack && 
            millis() >= effectState.timeCountdownInit + touchState.lastTouchDuration) {
            sendResolumeInitOSC(5);
            effectState.waitInitAfterBack = false;
            if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                Serial.println("[OSC->Resolume] InitOSC sent after BackOSC delay!");
                xSemaphoreGive(serialMutex);
            }
        }
        
        // Handle main effect
        if (effectState.waitingMainEffect) {
            effectState.effectEnable = false;
            sendResolumeMain(5);
            rainbowCaterpillarEffect(MAIN_EFFECT_TIME);
            sendResolumeInitOSC(5);
            
            // Reset states
            touchState.touchStartMillis = 0;
            effectState.waitingMainEffect = false;
            effectState.mainEffectStarted = false;
            effectState.effectEnable = true;
            touchState.isTouched = false;
            touchState.sentOSCOnce = false;
            touchState.latestStatus = -1;
            touchState.latestValue = -1;
        }
        
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

void effectUpdateTask(void *parameter) {
    TickType_t lastWakeTime = xTaskGetTickCount();
    
    while (true) {
        // Update rainbow effect if active
        updateRainbowEffect();
        
        // Delay for next update
        vTaskDelayUntil(&lastWakeTime, pdMS_TO_TICKS(UPDATE_INTERVAL));
    }
}