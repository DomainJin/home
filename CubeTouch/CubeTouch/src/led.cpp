#include "led.h"

void initLEDs() {
    strip.begin();
    strip.show();
    
    // Initial LED test
    setAllLEDs(50, 50, 50); // Dim white
    delay(1000);
    setAllLEDs(0, 0, 0); // Off
}

void setAllLEDs(uint8_t r, uint8_t g, uint8_t b) {
    for (int i = 0; i < LED_COUNT; i++) {
        strip.setPixelColor(i, strip.Color(r, g, b));
    }
    strip.show();
}

void runLEDEffect() {
    static unsigned long lastUpdate = 0;
    static int effectStep = 0;
    
    if (millis() - lastUpdate < 50) return;
    lastUpdate = millis();
    
    switch (currentEffect) {
        case 0: // Solid color
            setAllLEDs(currentRed, currentGreen, currentBlue);
            break;
            
        case 1: // Rainbow
            rainbowEffect(effectStep);
            effectStep = (effectStep + 2) % 256;
            break;
            
        case 2: // Running light
            runningLight(effectStep);
            effectStep = (effectStep + 1) % LED_COUNT;
            break;
            
        case 3: // Breathing
            breathingEffect(effectStep);
            effectStep = (effectStep + 2) % 256;
            break;
    }
}

void rainbowEffect(int step) {
    for (int i = 0; i < LED_COUNT; i++) {
        int hue = (i * 256 / LED_COUNT + step) % 256;
        uint32_t color = strip.gamma32(strip.ColorHSV(hue * 256));
        strip.setPixelColor(i, color);
    }
    strip.show();
}

void runningLight(int position) {
    strip.clear();
    for (int i = 0; i < 5; i++) {
        int pos = (position + i) % LED_COUNT;
        int brightness = 255 - (i * 50);
        strip.setPixelColor(pos, strip.Color(brightness, 0, brightness));
    }
    strip.show();
}

void breathingEffect(int step) {
    int brightness = (sin(step * 0.024) + 1) * 127;
    setAllLEDs(brightness, brightness/2, 0);
}