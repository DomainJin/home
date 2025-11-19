#include <WiFi.h>
#include <OSCMessage.h>
#include <WiFiUdp.h>
#include <Adafruit_NeoPixel.h>




#define mainEffectTime 6000
#define operationTime 2000
#define LED_PIN     5        
#define NUM_LEDS    150      




Adafruit_NeoPixel strip(NUM_LEDS, LED_PIN, NEO_BGR + NEO_KHZ400);
// WiFi và OSC
const char* ssid = "Cube Touch";
const char* password = "admin123";




WiFiUDP UdpPortSend;
WiFiUDP udp;




// Địa chỉ và cổng OSC laptop và Resolume




const IPAddress resolume_ip(192, 168, 0, 241);
const unsigned int resolume_port = 7000;




const IPAddress laptop_ip(192, 168, 0, 159);
const unsigned int laptop_port = 7000;
unsigned int localUdpPort = 4210;




char incomingPacket[255];  
int brightness = 255;    // Độ sáng mặc định (0-255)
int last_r = 43, last_g = 159, last_b = 2;   // Lưu màu cuối cùng
bool configMode = false; // Config mode - cho phép điều khiển LED từ xa




// UART buffer và trạng thái
String uartBuffer = "";
String uartLabel = "";
HardwareSerial SerialPIC(1);




bool waitingMainEffect = false;
bool waitInitAfterBack = false;
unsigned long mainEffectStartMillis = 0;
bool mainEffectStarted = false; // mới thêm
// Trạng thái touch/value
bool isTouched = false;
bool sentOSCOnce = false;
unsigned long touchStartMillis = 0;
unsigned long lastTouchDuration = 0;
unsigned long timeCountdownInit = 0;
int latestStatus = -1;
int latestValue = -1;




int UPDATE_INTERVAL = operationTime/NUM_LEDS; // ms




int currentLedCount = 0;           // Số lượng led đang sáng
unsigned long lastUpdateTime = 0;  // Thời gian cập nhật
bool effectEnable = true;
int ledDirection = 1;  
             // Chiều LED: 1 = bình thường, 0 = đảo ngược
void applyColorWithBrightness(bool turnOn, int r, int g, int b) {
  if (!effectEnable) return;
  unsigned long now = millis();
  if (now - lastUpdateTime >= UPDATE_INTERVAL) {
    lastUpdateTime = now;
    // Sáng dần
    if (turnOn && currentLedCount < NUM_LEDS) {
      currentLedCount++;
    }
    // Tắt dần
    else if (!turnOn && currentLedCount > 0) {
      currentLedCount--;
    }
    // Dùng brightness để tính màu từng led
    int adj_r = r * brightness / 255;
    int adj_g = g * brightness / 255;
    int adj_b = b * brightness / 255;
    // Sáng/tắt từng led
    if(ledDirection == 1){
    for (int i = 0; i < NUM_LEDS; i++) {
      if (i < currentLedCount)
        strip.setPixelColor(i, strip.Color(adj_r, adj_g, adj_b));
      else
        strip.setPixelColor(i, strip.Color(0, 0, 0));
      }
    }
    else{
      for (int i = 0; i < NUM_LEDS; i++) {
          if (i >= NUM_LEDS - currentLedCount)
              strip.setPixelColor(i, strip.Color(adj_r, adj_g, adj_b));
          else
              strip.setPixelColor(i, strip.Color(0, 0, 0));
      }
    }


    strip.show();
  }
}




void disableEffect() {
  effectEnable = false;
  currentLedCount = 0;
  for (int i = 0; i < NUM_LEDS; i++)
    strip.setPixelColor(i, strip.Color(0,0,0));
  strip.show();
}
// State machine cho rainbow effect thay vì blocking loop
bool rainbowEffectActive = false;
unsigned long rainbowStartTime = 0;
int rainbowOffset = 0;

void startRainbowEffect() {
  rainbowEffectActive = true;
  rainbowStartTime = millis();
  rainbowOffset = 0;
  Serial.println("Rainbow effect started!");
}
void rainbowCaterpillarEffect(unsigned long durationSec) {
  unsigned long startTime = millis();
  int rainbowOffset = 0;
  while (millis() - startTime < durationSec) {
    for (int i = 0; i < NUM_LEDS; i++) {
      uint8_t pixelHue = (rainbowOffset + i * (255 / 7)) % 255;
      uint32_t color = strip.gamma32(strip.ColorHSV(pixelHue * 256));
      strip.setPixelColor(i, color);
    }
    strip.show();
    rainbowOffset = (rainbowOffset + 4) % 255;
    delay(UPDATE_INTERVAL);
  }
  // Tắt LED sau khi chạy xong
  for (int i = 0; i < NUM_LEDS; i++) strip.setPixelColor(i, 0);
  strip.show();
}

void updateRainbowEffect() {
  if (!rainbowEffectActive) return;
  
  unsigned long elapsed = millis() - rainbowStartTime;
  if (elapsed >= mainEffectTime) {
    // Kết thúc effect
    rainbowEffectActive = false;
    for (int i = 0; i < NUM_LEDS; i++) strip.setPixelColor(i, 0);
    strip.show();
    Serial.println("Rainbow effect finished!");
    return;
  }
  
  // Cập nhật rainbow mỗi UPDATE_INTERVAL
  static unsigned long lastRainbowUpdate = 0;
  if (millis() - lastRainbowUpdate >= UPDATE_INTERVAL) {
    lastRainbowUpdate = millis();
    
    for (int i = 0; i < NUM_LEDS; i++) {
      uint8_t pixelHue = (rainbowOffset + i * (255 / 7)) % 255;
      uint32_t color = strip.gamma32(strip.ColorHSV(pixelHue * 256));
      strip.setPixelColor(i, color);
    }
    strip.show();
    rainbowOffset = (rainbowOffset + 4) % 255;
  }
}




// Gửi OSC debug: luôn gửi cặp trạng thái + giá trị cảm biến
void sendDebugOSCString(const String& message) {
 
  OSCMessage msg("/debug");
  msg.add(message.c_str());   // Gửi thành 1 argument kiểu chuỗi
  UdpPortSend.beginPacket(laptop_ip, laptop_port);
  msg.send(UdpPortSend);
  UdpPortSend.endPacket();
  msg.empty();
}




void sendResolumeEnableOSC(int durationMs) {
  unsigned long startTime = millis();
  while (millis() - startTime < durationMs) {
    OSCMessage msg1("/composition/layers/1/clear");
    msg1.add((int32_t)1);
    OSCMessage msg2("/composition/layers/1/clips/2/connect");
    msg2.add((int32_t)1);
    OSCMessage msg3("/composition/layers/1/clips/2/transport/position/behaviour/playdirection");
    msg3.add((int32_t)2);


    OSCMessage msg4("/composition/layers/2/clear");
    msg4.add((int32_t)1);
    OSCMessage msg5("/composition/layers/2/clips/2/connect");
    msg5.add((int32_t)1);
    OSCMessage msg6("/composition/layers/2/clips/2/transport/position/behaviour/playdirection");
    msg6.add((int32_t)2);


    OSCMessage msg7("/composition/layers/3/clear");
    msg7.add((int32_t)1);
    OSCMessage msg8("/composition/layers/3/clips/2/connect");
    msg8.add((int32_t)1);
    OSCMessage msg9("/composition/layers/3/clips/2/transport/position/behaviour/playdirection");
    msg9.add((int32_t)2);




    UdpPortSend.beginPacket(resolume_ip, resolume_port); msg1.send(UdpPortSend); UdpPortSend.endPacket(); msg1.empty();
    UdpPortSend.beginPacket(resolume_ip, resolume_port); msg2.send(UdpPortSend); UdpPortSend.endPacket(); msg2.empty();
    UdpPortSend.beginPacket(resolume_ip, resolume_port); msg3.send(UdpPortSend); UdpPortSend.endPacket(); msg3.empty();
    UdpPortSend.beginPacket(resolume_ip, resolume_port); msg4.send(UdpPortSend); UdpPortSend.endPacket(); msg4.empty();
    UdpPortSend.beginPacket(resolume_ip, resolume_port); msg5.send(UdpPortSend); UdpPortSend.endPacket(); msg5.empty();
    UdpPortSend.beginPacket(resolume_ip, resolume_port); msg6.send(UdpPortSend); UdpPortSend.endPacket(); msg6.empty();
    UdpPortSend.beginPacket(resolume_ip, resolume_port); msg7.send(UdpPortSend); UdpPortSend.endPacket(); msg7.empty();
    UdpPortSend.beginPacket(resolume_ip, resolume_port); msg8.send(UdpPortSend); UdpPortSend.endPacket(); msg8.empty();
    UdpPortSend.beginPacket(resolume_ip, resolume_port); msg9.send(UdpPortSend); UdpPortSend.endPacket(); msg9.empty();


    Serial.println("[OSC->Resolume] Enable clips sent!");
   
  }
}
void sendResolumeInitOSC(int durationMs) {
  unsigned long startTime = millis();
  while (millis() - startTime < durationMs) {
    OSCMessage msga("/composition/layers/1/clips/1/connect");
    msga.add((int32_t)1);
    OSCMessage msgs("/composition/layers/1/clips/1/transport/position/behaviour/playdirection");
    msgs.add((int32_t)2);
    OSCMessage msgd("/composition/layers/2/clips/1/connect");
    msgd.add((int32_t)1);
    OSCMessage msgf("/composition/layers/2/clips/1/transport/position/behaviour/playdirection");
    msgf.add((int32_t)2);
    OSCMessage msgg("/composition/layers/3/clips/1/connect");
    msgg.add((int32_t)1);
    OSCMessage msgh("/composition/layers/3/clips/1/transport/position/behaviour/playdirection");
    msgh.add((int32_t)2);


    UdpPortSend.beginPacket(resolume_ip, resolume_port); msga.send(UdpPortSend); UdpPortSend.endPacket(); msga.empty();
    UdpPortSend.beginPacket(resolume_ip, resolume_port); msgs.send(UdpPortSend); UdpPortSend.endPacket(); msgs.empty();
    UdpPortSend.beginPacket(resolume_ip, resolume_port); msgd.send(UdpPortSend); UdpPortSend.endPacket(); msgd.empty();
    UdpPortSend.beginPacket(resolume_ip, resolume_port); msgf.send(UdpPortSend); UdpPortSend.endPacket(); msgf.empty();
    UdpPortSend.beginPacket(resolume_ip, resolume_port); msgg.send(UdpPortSend); UdpPortSend.endPacket(); msgg.empty();
    UdpPortSend.beginPacket(resolume_ip, resolume_port); msgh.send(UdpPortSend); UdpPortSend.endPacket(); msgh.empty();


    Serial.println("[OSC->Resolume] Enable clips sent!");
   
  }
}
void sendResolumeBackOSC(int durationMs) {
  unsigned long startTime = millis();
  while (millis() - startTime < durationMs) {
    OSCMessage msgq("/composition/layers/1/clips/2/transport/position/behaviour/playdirection");
    msgq.add((int32_t)0);
    OSCMessage msgw("/composition/layers/2/clips/2/transport/position/behaviour/playdirection");
    msgw.add((int32_t)0);
    OSCMessage msge("/composition/layers/3/clips/2/transport/position/behaviour/playdirection");
    msge.add((int32_t)0);
    UdpPortSend.beginPacket(resolume_ip, resolume_port); msgq.send(UdpPortSend); UdpPortSend.endPacket(); msgq.empty();
    UdpPortSend.beginPacket(resolume_ip, resolume_port); msgw.send(UdpPortSend); UdpPortSend.endPacket(); msgw.empty();
    UdpPortSend.beginPacket(resolume_ip, resolume_port); msge.send(UdpPortSend); UdpPortSend.endPacket(); msge.empty();
    Serial.println("[OSC->Resolume] Back clips sent!");
   
  }
}


void sendResolumeMain(int durationMs){
  unsigned long startTime = millis();
  while (millis() - startTime < durationMs) {
    OSCMessage msgz("/composition/layers/3/clips/3/connect");
    msgz.add((int32_t)1);
    OSCMessage msgx("/composition/layers/3/clips/3/transport/position/behaviour/playdirection");
    msgx.add((int32_t)2);


    UdpPortSend.beginPacket(resolume_ip, resolume_port); msgz.send(UdpPortSend); UdpPortSend.endPacket(); msgz.empty();
    UdpPortSend.beginPacket(resolume_ip, resolume_port); msgx.send(UdpPortSend); UdpPortSend.endPacket(); msgx.empty();


    Serial.println("[OSC->Resolume] Main effect sent!");


  }
}




void setup() {
  strip.begin();
  strip.show();
  strip.setBrightness(brightness);








  Serial.begin(115200);
  SerialPIC.begin(9600, SERIAL_8N1, 33, 26);








  Serial.println("ESP32 Ready to receive from PIC!");
  WiFi.begin(ssid, password);
  int attempt = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    attempt++;
    if (attempt > 30) {
      Serial.println("Kết nối WiFi thất bại!");
      while(1);
    }
  }
  Serial.println("\nWiFi connected!");
  Serial.print("Local IP: "); Serial.println(WiFi.localIP());
  UdpPortSend.begin(9000);
  udp.begin(localUdpPort);
  Serial.printf("Listening UDP on port %d\n", localUdpPort);
}




void loop() {




  int packetSize = udp.parsePacket();
  if (packetSize) {
    int len = udp.read(incomingPacket, 254);
    incomingPacket[len] = 0;
    Serial.printf("Received: %s\n", incomingPacket);
    // Kiểm tra lệnh config mode
    if (strncmp(incomingPacket, "CONFIG:", 7) == 0) {
      int configState = atoi(incomingPacket + 7);
      configMode = (configState == 1);
      if (configMode) {
        touchProcessingDisabled = true; // Tắt xử lý chạm khi config
        effectEnable = true; // Bật LED để điều khiển
      } else {
        touchProcessingDisabled = false; // Bật lại xử lý chạm
      }
      Serial.printf("Config Mode: %s\n", configMode ? "ON" : "OFF");
    }
    // Kiểm tra lệnh điều khiển LED trực tiếp (chỉ hoạt động trong config mode)
    else if (strncmp(incomingPacket, "LEDCTRL:", 8) == 0 && configMode) {
      String command = String(incomingPacket + 8);
      int firstComma = command.indexOf(',');
      int secondComma = command.indexOf(',', firstComma + 1);
      int thirdComma = command.indexOf(',', secondComma + 1);
      
      if (firstComma > 0 && secondComma > 0 && thirdComma > 0) {
        String indexStr = command.substring(0, firstComma);
        int r = command.substring(firstComma + 1, secondComma).toInt();
        int g = command.substring(secondComma + 1, thirdComma).toInt();
        int b = command.substring(thirdComma + 1).toInt();
        
        if (indexStr == "ALL") {
          // Điều khiển tất cả LED
          for (int i = 0; i < NUM_LEDS; i++) {
            strip.setPixelColor(i, strip.Color(r, g, b));
          }
        } else {
          // Điều khiển LED cụ thể
          int index = indexStr.toInt();
          if (index >= 0 && index < NUM_LEDS) {
            strip.setPixelColor(index, strip.Color(r, g, b));
          }
        }
        strip.show();
        Serial.printf("Direct LED Control: %s R=%d G=%d B=%d\n", indexStr.c_str(), r, g, b);
      }
    }
    // Kiểm tra lệnh rainbow effect (chỉ hoạt động trong config mode)
    else if (strcmp(incomingPacket, "RAINBOW:START") == 0 && configMode) {
      startRainbowEffect();
      Serial.println("Rainbow effect started via config mode");
    }
    // Kiểm tra lệnh bật/tắt LED
    else if (strncmp(incomingPacket, "LED:", 4) == 0) {
      int ledState = atoi(incomingPacket + 4);
      effectEnable = (ledState == 1);
      if (!effectEnable) {
        // Tắt tất cả LED khi disable
        for (int i = 0; i < NUM_LEDS; i++)
          strip.setPixelColor(i, strip.Color(0,0,0));
        strip.show();
        currentLedCount = 0;
      }
      Serial.printf("LED Control: %s\n", effectEnable ? "ON" : "OFF");
    }
    // Kiểm tra lệnh điều khiển chiều LED
    else if (strncmp(incomingPacket, "DIR:", 4) == 0) {
      int direction = atoi(incomingPacket + 4);
      ledDirection = (direction == 1) ? 1 : 0;
      Serial.printf("LED Direction: %d\n", ledDirection);
    }
    // Kiểm tra lệnh thiết lập ngưỡng
    else if (strncmp(incomingPacket, "THRESHOLD:", 10) == 0) {
      int thresholdValue = atoi(incomingPacket + 10);
      // Gửi giá trị ngưỡng xuống PIC qua UART với format mới
      SerialPIC.print("THRESHOLD:");
      SerialPIC.print(thresholdValue);
      SerialPIC.print("\n");
      Serial.printf("Sent threshold to PIC: %d\n", thresholdValue);
    }
    // Kiểm tra lệnh tăng/giảm độ sáng
    else if (strcmp(incomingPacket, "UP") == 0) {
      brightness += 16;
      if (brightness > 255) brightness = 255;
      Serial.printf("Brightness UP: %d\n", brightness);
    }
    else if (strcmp(incomingPacket, "DOWN") == 0) {
      brightness -= 16;
      if (brightness < 1) brightness = 1;
     
      Serial.printf("Brightness DOWN: %d\n", brightness);
    }
    // Nếu nhận chuỗi màu
    else {
      int r, g, b;
      if (sscanf(incomingPacket, "%d %d %d", &r, &g, &b) == 3) {
        last_r = r; last_g = g; last_b = b;
        Serial.printf("Set color: R=%d G=%d B=%d, Brightness=%d\n", r, g, b, brightness);
      }
    }
  }




  // Cập nhật rainbow effect nếu đang chạy
  updateRainbowEffect();
  
  // Chỉ áp dụng LED bình thường khi không có rainbow effect
  if (!rainbowEffectActive) {
    strip.setBrightness(brightness);
    applyColorWithBrightness(isTouched, last_r, last_g, last_b);
  }

  if (isTouched && !mainEffectStarted && (millis() - touchStartMillis >= operationTime)) {
    waitingMainEffect = true;
    mainEffectStarted = true;
    Serial.println("Set waitingMainEffect = true (chạm đủ lâu)");
  }

  if(waitingMainEffect) {
    effectEnable = false;
    sendResolumeMain(5);
    Serial.print(" | Main effect triggered!");
    rainbowCaterpillarEffect(mainEffectTime);
    Serial.println("[OSC->Resolume] Main effect started, non-blocking rainbow.");
    sendResolumeInitOSC(5);
    touchStartMillis = 0;
    waitingMainEffect = false;
    mainEffectStarted = false;  
    effectEnable = true;
    isTouched = false;
    sentOSCOnce = false;
    latestStatus = -1;
    latestValue = -1;
  }
  if (waitInitAfterBack && millis() >= timeCountdownInit + lastTouchDuration) {
    sendResolumeInitOSC(5);
    waitInitAfterBack = false; // Reset lại cờ
    Serial.println("[OSC->Resolume] InitOSC sent after BackOSC delay!");
  }
  while (SerialPIC.available()) {
    char c = SerialPIC.read();
    if (c == '\n') {
      uartBuffer.trim();
      sendDebugOSCString(uartBuffer);
      if (uartBuffer == "value") {
        uartLabel = "value";
      } else if (uartBuffer == "status") {
        uartLabel = "status";
      } else {
        if (uartLabel == "value") {
          latestValue = uartBuffer.toInt();
        } else if (uartLabel == "status") {
          latestStatus = uartBuffer.toInt();
        }
        uartLabel = "";
      }
      uartBuffer = "";




      // Chỉ gửi khi cả giá trị và trạng thái đã nhận đủ từ PIC
      if (latestStatus != -1 && latestValue != -1) {
       
        // Debug UART: in trạng thái, giá trị, thời gian chạm nếu có
        Serial.print("[UART Debug] Status: ");
        Serial.print(latestStatus ? "Touched" : "None");
        Serial.print(" | Value: ");
        Serial.print(latestValue);




        if (latestStatus == 1) {
          if (!isTouched) {
            isTouched = true;
            sentOSCOnce = false;
            touchStartMillis = millis();
            Serial.print(" | Touch detected!");
           
          }
          if (!sentOSCOnce) {
            sendResolumeEnableOSC(5);
            sentOSCOnce = true;
          }
        } else {
          if (isTouched) {
            isTouched = false;
            sentOSCOnce = false;
            lastTouchDuration = millis() - touchStartMillis;
            Serial.print(" | Touch duration: ");
            Serial.print(lastTouchDuration);




            if (lastTouchDuration < operationTime && lastTouchDuration > 0) {
              timeCountdownInit = millis();
              sendResolumeBackOSC(5);
              Serial.print(" | Send BackOSC (touch < )");
              Serial.print(operationTime);
              waitInitAfterBack = true;
            }
           
            else if (lastTouchDuration >= operationTime) {
            sendResolumeMain(5);
            waitingMainEffect = true;
            mainEffectStartMillis = millis();
            Serial.print(" | Main effect triggered!");
            }
           
          }
        }
        Serial.println();




       




        // Reset biến nhận cho lần tiếp theo
        latestStatus = -1;
        latestValue = -1;
      }
     
     
    } else {
     
      uartBuffer += c;
    }
  }
  // Có thể bổ sung gửi trạng thái định kỳ/timer ở đây nếu muốn
}






