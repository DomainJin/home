#include "customOSC.h"

SimpleOSCMessage::SimpleOSCMessage(const char* addr) {
    address = String(addr);
    hasInt = false;
    hasString = false;
    intValue = 0;
    stringValue = "";
}

void SimpleOSCMessage::add(const char* str) {
    stringValue = String(str);
    hasString = true;
}

void SimpleOSCMessage::add(int32_t value) {
    intValue = value;
    hasInt = true;
}

void SimpleOSCMessage::writeString(uint8_t* buffer, int& offset, const String& str) {
    int len = str.length();
    memcpy(buffer + offset, str.c_str(), len);
    offset += len;
    
    // Null terminator
    buffer[offset++] = 0;
    
    // Pad to 4-byte boundary
    while (offset % 4 != 0) {
        buffer[offset++] = 0;
    }
}

void SimpleOSCMessage::writeInt32(uint8_t* buffer, int& offset, int32_t value) {
    // Big endian format
    buffer[offset++] = (value >> 24) & 0xFF;
    buffer[offset++] = (value >> 16) & 0xFF;
    buffer[offset++] = (value >> 8) & 0xFF;
    buffer[offset++] = value & 0xFF;
}

void SimpleOSCMessage::padToMultiple4(uint8_t* buffer, int& offset) {
    while (offset % 4 != 0) {
        buffer[offset++] = 0;
    }
}

void SimpleOSCMessage::send(WiFiUDP& udp) {
    uint8_t buffer[256];
    int offset = 0;
    
    // Write OSC Address
    writeString(buffer, offset, address);
    
    // Write Type Tag String
    String typeTag = ",";
    if (hasInt) typeTag += "i";
    if (hasString) typeTag += "s";
    writeString(buffer, offset, typeTag);
    
    // Write Arguments
    if (hasInt) {
        writeInt32(buffer, offset, intValue);
    }
    if (hasString) {
        writeString(buffer, offset, stringValue);
    }
    
    // Send the packet
    udp.write(buffer, offset);
}

void SimpleOSCMessage::empty() {
    hasInt = false;
    hasString = false;
    intValue = 0;
    stringValue = "";
}