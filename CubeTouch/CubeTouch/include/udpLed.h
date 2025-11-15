#ifndef UDP_LED_H
#define UDP_LED_H

#include "main.h"

// UDP communication functions
void initUDP();
void handleUDP();
void processCommand(JsonDocument& doc);
void sendResponse(String message);
void sendStatus();

#endif