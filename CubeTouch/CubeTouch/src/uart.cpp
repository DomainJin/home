#include "uart.h"

void initUART() {
    // Initialize UART serial communication on pins 26, 33
    uartSerial.begin(UART_BAUD, SERIAL_8N1, UART_RX_PIN, UART_TX_PIN);
    
    if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
        Serial.printf("UART module initialized: TX=%d, RX=%d, Baud=%d\n", 
                      UART_TX_PIN, UART_RX_PIN, UART_BAUD);
        Serial.println("Ready to receive data from PIC...");
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
    String buffer = "";
    
    while (1) {
        if (uartSerial.available()) {
            while (uartSerial.available()) {
                char incomingByte = uartSerial.read();
                
                if (incomingByte >= 32 && incomingByte <= 126) {
                    buffer += incomingByte;
                }
                
                if (incomingByte == '\n' || incomingByte == '\r' || buffer.length() >= 10) {
                    if (buffer.length() > 0) {
                        buffer.trim();
                        
                        // Send event to queue
                        CustomEvent_t event;
                        event.type = EVENT_UART_DATA;
                        event.data = buffer;
                        
                        if (xQueueSend(eventQueue, &event, pdMS_TO_TICKS(100)) != pdTRUE) {
                            if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                                Serial.println("Failed to send UART event!");
                                xSemaphoreGive(serialMutex);
                            }
                        }
                        
                        buffer = "";
                    }
                }
                
                if (buffer.length() > 20) {
                    buffer = "";
                }
            }
        }
        
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

void handleUART() {
    // Legacy function - now handled by uartTask
}