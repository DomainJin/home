#ifndef LED_H
#define LED_H

#include "main.h"

// LED control functions
void initLEDs();
void setAllLEDs(uint8_t r, uint8_t g, uint8_t b);
void runLEDEffect();
void rainbowEffect(int step);
void runningLight(int position);
void breathingEffect(int step);

#endif