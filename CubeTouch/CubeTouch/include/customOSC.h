#ifndef CUSTOM_OSC_H
#define CUSTOM_OSC_H

#include <Arduino.h>
#include <WiFiUdp.h>

class SimpleOSCMessage {
private:
    String address;
    String stringValue;
    int32_t intValue;
    bool hasInt;
    bool hasString;
    
public:
    SimpleOSCMessage(const char* addr);
    void add(const char* str);
    void add(int32_t value);
    void send(WiFiUDP& udp);
    void empty();
    
private:
    void writeString(uint8_t* buffer, int& offset, const String& str);
    void writeInt32(uint8_t* buffer, int& offset, int32_t value);
    void padToMultiple4(uint8_t* buffer, int& offset);
};

#endif