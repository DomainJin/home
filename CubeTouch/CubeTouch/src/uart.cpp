#include "uart.h"
#include "touchEvent.h"

void initUART() {
    // SerialPIC is already initialized in main.cpp setup()
    // Keep this for compatibility
    if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
        Serial.printf("UART module ready: TX=%d, RX=%d, Baud=%d\n", 
                      26, 33, 9600);
        Serial.println("Ready to receive touch data from PIC...");
        xSemaphoreGive(serialMutex);
    }
}

void sendUART(String data) {
    uartSerial.println(data);
    uartSerial.flush();
    
    if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
        Serial.printf("UART Sent: %s\n", data.c_str());
        xSemaphoreGive(serialMutex);
    }
}

// UART Task - runs on Core 1  
void uartTask(void *parameter) {
    // Use global variables from main.cpp
    extern String uartBuffer;
    extern String uartLabel;
    extern int latestStatus;
    extern int latestValue;
    extern bool touchProcessingDisabled;
    extern HardwareSerial SerialPIC;
    
    while (1) {
        // Process UART data exactly like main1.ino
        while (SerialPIC.available()) {
            char c = SerialPIC.read();
            if (c == '\n') {
                uartBuffer.trim();
                
                if (uartBuffer == "value") {
                    uartLabel = "value";
                } else if (uartBuffer == "status") {
                    uartLabel = "status";
                } else {
                    bool dataUpdated = false;
                    
                    if (uartLabel == "value") {
                        int newValue = uartBuffer.toInt();
                        if (newValue != latestValue) {
                            latestValue = newValue;
                            dataUpdated = true;
                        }
                    } else if (uartLabel == "status") {
                        int newStatus = uartBuffer.toInt();
                        if (newStatus != latestStatus) {
                            latestStatus = newStatus;
                            dataUpdated = true;
                        }
                    }
                    
                    uartLabel = "";
                    
                    // Debug output
                    if (dataUpdated) {
                        if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                            Serial.printf("[UART] Status: %d, Value: %d\n", latestStatus, latestValue);
                            xSemaphoreGive(serialMutex);
                        }
                        
                        // Process touch data when updated
                        if (!touchProcessingDisabled && latestStatus >= 0 && latestValue >= 0) {
                            processTouchData(latestStatus, latestValue);
                        }
                    }
                }
                uartBuffer = "";
            } else {
                uartBuffer += c;
            }
        }
        
        vTaskDelay(pdMS_TO_TICKS(5)); // Fast polling for touch data
    }
}

void handleUART() {
    // Legacy function - now handled by uartTask
}