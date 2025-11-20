#ifndef TOUCH_EVENT_H
#define TOUCH_EVENT_H

#include "main.h"
#include "customOSC.h"

// Touch event constants
#define MAIN_EFFECT_TIME 6000
#define OPERATION_TIME 2000
#define OSC_INTERVAL 100
#define UPDATE_INTERVAL 5

// OSC targets
extern const IPAddress resolume_ip;
extern const unsigned int resolume_port;
extern const unsigned int laptop_port;

// Touch state structure
typedef struct {
    bool isTouched;
    bool sentOSCOnce;
    unsigned long touchStartMillis;
    unsigned long lastTouchDuration;
    int latestStatus;
    int latestValue;
    unsigned long lastOSCTime;
    int lastSentStatus;
    int lastSentValue;
} TouchState_t;

// Effect control structure
typedef struct {
    bool waitingMainEffect;
    bool waitInitAfterBack;
    unsigned long mainEffectStartMillis;
    unsigned long timeCountdownInit;
    bool mainEffectStarted;
    bool effectEnable;
    int ledDirection;
    bool rainbowEffectActive;
    unsigned long rainbowStartTime;
    int rainbowOffset;
} EffectState_t;

// Touch event types
typedef enum {
    TOUCH_EVENT_NONE,
    TOUCH_EVENT_START,
    TOUCH_EVENT_END,
    TOUCH_EVENT_SHORT,
    TOUCH_EVENT_LONG
} TouchEventType_t;

// Touch event structure for FreeRTOS
typedef struct {
    TouchEventType_t type;
    int value;
    int status;
    unsigned long duration;
    unsigned long timestamp;
} TouchEvent_t;

// Global touch and effect states
extern TouchState_t touchState;
extern EffectState_t effectState;

// Touch processing functions
void initTouchSystem();
void processTouchData(int status, int value);
void handleTouchEvent(TouchEvent_t* event);
void sendDebugOSCString(const String& message);
void sendResolumeEnableOSC(int durationMs);
void sendResolumeInitOSC(int durationMs);
void sendResolumeBackOSC(int durationMs);
void sendResolumeMain(int durationMs);

// Effect functions
void updateRainbowEffect();
void rainbowCaterpillarEffect(unsigned long durationMs);
void startRainbowEffect();

// Task functions
void touchProcessingTask(void *parameter);
void effectUpdateTask(void *parameter);

#endif