#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "esp_netif.h"
#include "lwip/err.h"
#include "lwip/sys.h"
#include "lwip/sockets.h"
#include "lwip/netdb.h"
#include "driver/rmt.h"
#include "driver/gpio.h"

// WiFi credentials
#define WIFI_SSID "Cube Touch"
#define WIFI_PASS "admin123"

// OSC server configuration
#define OSC_SERVER_IP "192.168.0.159"
#define OSC_SERVER_PORT 7000

// Maximum retry count for WiFi connection
#define WIFI_MAXIMUM_RETRY 5

// WS2812 LED Strip Configuration
#define LED_STRIP_GPIO 5
#define LED_STRIP_LENGTH 100
#define RMT_CHANNEL RMT_CHANNEL_0

// WS2812 timing (in microseconds)
#define WS2812_T0H 350    // 0 bit high time
#define WS2812_T0L 800    // 0 bit low time
#define WS2812_T1H 700    // 1 bit high time
#define WS2812_T1L 600    // 1 bit low time
#define WS2812_RESET 50000 // Reset time

// RGB color structure
typedef struct {
    uint8_t red;
    uint8_t green;
    uint8_t blue;
} rgb_color_t;

static const char *TAG = "ESP32_OSC";
static int s_retry_num = 0;
static bool wifi_connected = false;

// Function prototypes
rgb_color_t hsv_to_rgb(int h, int s, int v);

// Event handler for WiFi events
static void event_handler(void* arg, esp_event_base_t event_base,
                         int32_t event_id, void* event_data)
{
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
    } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
        if (s_retry_num < WIFI_MAXIMUM_RETRY) {
            esp_wifi_connect();
            s_retry_num++;
            ESP_LOGI(TAG, "Retry to connect to the AP");
        } else {
            ESP_LOGI(TAG,"Connect to the AP fail");
        }
        wifi_connected = false;
    } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t* event = (ip_event_got_ip_t*) event_data;
        ESP_LOGI(TAG, "Got IP:" IPSTR, IP2STR(&event->ip_info.ip));
        s_retry_num = 0;
        wifi_connected = true;
    }
}

// Initialize WiFi in station mode
void wifi_init_sta(void)
{
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    esp_event_handler_instance_t instance_any_id;
    esp_event_handler_instance_t instance_got_ip;
    ESP_ERROR_CHECK(esp_event_handler_instance_register(WIFI_EVENT,
                                                        ESP_EVENT_ANY_ID,
                                                        &event_handler,
                                                        NULL,
                                                        &instance_any_id));
    ESP_ERROR_CHECK(esp_event_handler_instance_register(IP_EVENT,
                                                        IP_EVENT_STA_GOT_IP,
                                                        &event_handler,
                                                        NULL,
                                                        &instance_got_ip));

    wifi_config_t wifi_config = {
        .sta = {
            .ssid = WIFI_SSID,
            .password = WIFI_PASS,
            .threshold.authmode = WIFI_AUTH_WPA2_PSK,
            .pmf_cfg = {
                .capable = true,
                .required = false
            },
        },
    };
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());

    ESP_LOGI(TAG, "WiFi init finished.");
}

// WS2812 LED Strip Functions
static rmt_item32_t led_data_buffer[LED_STRIP_LENGTH * 24]; // 24 bits per LED

// Convert RGB color to RMT format
static void rgb_to_rmt_item32(rgb_color_t color, rmt_item32_t* items) {
    uint32_t bits_to_send = (color.green << 16) | (color.red << 8) | color.blue;
    
    for (int bit = 0; bit < 24; bit++) {
        uint32_t bit_is_set = bits_to_send & (1 << (23 - bit));
        items[bit] = bit_is_set ?
            (rmt_item32_t){{{WS2812_T1H, 1, WS2812_T1L, 0}}} :
            (rmt_item32_t){{{WS2812_T0H, 1, WS2812_T0L, 0}}};
    }
}

// Initialize WS2812 LED strip
esp_err_t led_strip_init(void) {
    rmt_config_t rmt_cfg = {
        .rmt_mode = RMT_MODE_TX,
        .channel = RMT_CHANNEL,
        .clk_div = 2,
        .gpio_num = LED_STRIP_GPIO,
        .mem_block_num = 3,
        .tx_config = {
            .loop_en = false,
            .carrier_en = false,
            .idle_output_en = true,
            .idle_level = 0,
        }
    };
    
    esp_err_t ret = rmt_config(&rmt_cfg);
    if (ret != ESP_OK) {
        return ret;
    }
    
    return rmt_driver_install(rmt_cfg.channel, 0, 0);
}

// Set color for all LEDs
void led_strip_set_all(rgb_color_t color) {
    for (int i = 0; i < LED_STRIP_LENGTH; i++) {
        rgb_to_rmt_item32(color, &led_data_buffer[i * 24]);
    }
    rmt_write_items(RMT_CHANNEL, led_data_buffer, LED_STRIP_LENGTH * 24, false);
}

// Set color for specific LED
void led_strip_set_pixel(int pixel, rgb_color_t color) {
    if (pixel >= 0 && pixel < LED_STRIP_LENGTH) {
        rgb_to_rmt_item32(color, &led_data_buffer[pixel * 24]);
    }
}

// Update LED strip (send data to LEDs)
void led_strip_update(void) {
    rmt_write_items(RMT_CHANNEL, led_data_buffer, LED_STRIP_LENGTH * 24, false);
}

// Clear all LEDs
void led_strip_clear(void) {
    rgb_color_t black = {0, 0, 0};
    led_strip_set_all(black);
}

// Rainbow effect
void led_rainbow_effect(int offset) {
    for (int i = 0; i < LED_STRIP_LENGTH; i++) {
        int hue = (i * 360 / LED_STRIP_LENGTH + offset) % 360;
        rgb_color_t color = hsv_to_rgb(hue, 255, 100);
        led_strip_set_pixel(i, color);
    }
    led_strip_update();
}

// Convert HSV to RGB
rgb_color_t hsv_to_rgb(int h, int s, int v) {
    rgb_color_t rgb;
    unsigned char region, remainder, p, q, t;

    if (s == 0) {
        rgb.red = rgb.green = rgb.blue = v;
        return rgb;
    }

    region = h / 43;
    remainder = (h - (region * 43)) * 6;

    p = (v * (255 - s)) >> 8;
    q = (v * (255 - ((s * remainder) >> 8))) >> 8;
    t = (v * (255 - ((s * (255 - remainder)) >> 8))) >> 8;

    switch (region) {
        case 0:
            rgb.red = v; rgb.green = t; rgb.blue = p;
            break;
        case 1:
            rgb.red = q; rgb.green = v; rgb.blue = p;
            break;
        case 2:
            rgb.red = p; rgb.green = v; rgb.blue = t;
            break;
        case 3:
            rgb.red = p; rgb.green = q; rgb.blue = v;
            break;
        case 4:
            rgb.red = t; rgb.green = p; rgb.blue = v;
            break;
        default:
            rgb.red = v; rgb.green = p; rgb.blue = q;
            break;
    }

    return rgb;
}

// Running light effect
void led_running_light(int position, rgb_color_t color) {
    led_strip_clear();
    for (int i = 0; i < 5; i++) {  // 5 LED tail
        int led_pos = (position + i) % LED_STRIP_LENGTH;
        rgb_color_t dimmed_color = {
            color.red * (5 - i) / 5,
            color.green * (5 - i) / 5,
            color.blue * (5 - i) / 5
        };
        led_strip_set_pixel(led_pos, dimmed_color);
    }
    led_strip_update();
}

// Breathing effect
void led_breathing_effect(rgb_color_t base_color, float brightness) {
    rgb_color_t color = {
        (uint8_t)(base_color.red * brightness),
        (uint8_t)(base_color.green * brightness),
        (uint8_t)(base_color.blue * brightness)
    };
    led_strip_set_all(color);
}

// Create OSC message manually (simple implementation)
int create_osc_message(char* buffer, const char* address, const char* type_tag, float value) {
    int pos = 0;
    
    // OSC address
    int addr_len = strlen(address);
    strcpy(buffer + pos, address);
    pos += addr_len;
    
    // Pad to 4-byte boundary
    while (pos % 4 != 0) {
        buffer[pos++] = '\0';
    }
    
    // Type tag string
    buffer[pos++] = ',';
    strcpy(buffer + pos, type_tag);
    pos += strlen(type_tag);
    
    // Pad to 4-byte boundary
    while (pos % 4 != 0) {
        buffer[pos++] = '\0';
    }
    
    // Arguments (for float)
    if (strcmp(type_tag, "f") == 0) {
        // Convert float to big-endian 32-bit
        union { float f; uint32_t i; } converter;
        converter.f = value;
        uint32_t big_endian = __builtin_bswap32(converter.i);
        memcpy(buffer + pos, &big_endian, 4);
        pos += 4;
    }
    
    return pos;
}

// Send OSC message via UDP
void send_osc_message(const char* address, const char* type_tag, float value) {
    if (!wifi_connected) {
        ESP_LOGW(TAG, "WiFi not connected, cannot send OSC message");
        return;
    }

    char osc_buffer[256];
    int message_size = create_osc_message(osc_buffer, address, type_tag, value);
    
    // Create UDP socket
    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sock < 0) {
        ESP_LOGE(TAG, "Unable to create socket: errno %d", errno);
        return;
    }

    // Set destination address
    struct sockaddr_in dest_addr;
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(OSC_SERVER_PORT);
    inet_aton(OSC_SERVER_IP, &dest_addr.sin_addr);

    // Send OSC message
    int err = sendto(sock, osc_buffer, message_size, 0, 
                     (struct sockaddr *)&dest_addr, sizeof(dest_addr));
    if (err < 0) {
        ESP_LOGE(TAG, "Error occurred during sending: errno %d", errno);
    } else {
        ESP_LOGI(TAG, "OSC message sent: %s = %.2f", address, value);
    }

    close(sock);
}

// Task to send periodic OSC messages
void osc_sender_task(void *pvParameter) {
    float counter = 0.0;
    
    while (1) {
        if (wifi_connected) {
            // Send different OSC messages
            send_osc_message("/esp32/sensor1", "f", counter);
            send_osc_message("/esp32/sensor2", "f", counter * 2.0);
            send_osc_message("/esp32/heartbeat", "f", 1.0);
            
            counter += 0.1;
            if (counter > 100.0) {
                counter = 0.0;
            }
        }
        
        vTaskDelay(pdMS_TO_TICKS(1000)); // Send every 1 second
    }
}

// LED effects task
void led_effects_task(void *pvParameter) {
    int effect_mode = 0;
    int rainbow_offset = 0;
    int running_position = 0;
    float breathing_phase = 0.0;
    int effect_counter = 0; // Move outside the loop
    int color_index = 0;
    int hold_time = 0;
    
    rgb_color_t colors[] = {
        {255, 0, 0},    // Red
        {0, 255, 0},    // Green
        {0, 0, 255},    // Blue
        {255, 255, 0},  // Yellow
        {255, 0, 255},  // Magenta
        {0, 255, 255}   // Cyan
    };
    
    ESP_LOGI(TAG, "LED effects task started");
    
    while (1) {
        switch (effect_mode % 4) {
            case 0: // Rainbow effect
                led_rainbow_effect(rainbow_offset);
                rainbow_offset = (rainbow_offset + 5) % 360;
                vTaskDelay(pdMS_TO_TICKS(50));
                break;
                
            case 1: // Running light
                {
                    rgb_color_t current_color = colors[(running_position / 10) % 6];
                    led_running_light(running_position, current_color);
                    running_position = (running_position + 1) % LED_STRIP_LENGTH;
                    vTaskDelay(pdMS_TO_TICKS(100));
                }
                break;
                
            case 2: // Breathing effect
                {
                    float brightness = (sin(breathing_phase) + 1.0) / 2.0; // 0 to 1
                    rgb_color_t blue = {0, 50, 255};
                    led_breathing_effect(blue, brightness);
                    breathing_phase += 0.1;
                    vTaskDelay(pdMS_TO_TICKS(50));
                }
                break;
                
            case 3: // Static colors cycling
                led_strip_set_all(colors[color_index]);
                led_strip_update();
                
                hold_time++;
                if (hold_time >= 50) { // Change color every 2.5 seconds
                    color_index = (color_index + 1) % 6;
                    hold_time = 0;
                }
                vTaskDelay(pdMS_TO_TICKS(50));
                break;
        }
        
        // Change effect every 10 seconds
        effect_counter++;
        if (effect_counter >= 200) { // 200 * 50ms = 10 seconds
            effect_mode++;
            effect_counter = 0;
            rainbow_offset = 0;
            running_position = 0;
            breathing_phase = 0.0;
            ESP_LOGI(TAG, "Switching to LED effect mode: %d", effect_mode % 4);
        }
    }
}

void app_main(void)
{
    ESP_LOGI(TAG, "ESP32 OSC Sender with LED Strip Starting...");

    // Initialize NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    // Initialize LED strip
    ESP_LOGI(TAG, "Initializing LED strip...");
    ret = led_strip_init();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to initialize LED strip: %s", esp_err_to_name(ret));
    } else {
        ESP_LOGI(TAG, "LED strip initialized successfully");
        // Test LEDs with a quick flash
        rgb_color_t white = {50, 50, 50};
        led_strip_set_all(white);
        led_strip_update();
        vTaskDelay(pdMS_TO_TICKS(500));
        led_strip_clear();
        led_strip_update();
    }

    ESP_LOGI(TAG, "ESP_WIFI_MODE_STA");
    wifi_init_sta();

    // Wait a bit for WiFi to connect
    vTaskDelay(pdMS_TO_TICKS(5000));

    // Create OSC sender task
    xTaskCreate(&osc_sender_task, "osc_sender_task", 4096, NULL, 5, NULL);
    
    // Create LED effects task
    xTaskCreate(&led_effects_task, "led_effects_task", 4096, NULL, 4, NULL);

    ESP_LOGI(TAG, "ESP32 OSC Sender with LED Strip initialized successfully");
}
