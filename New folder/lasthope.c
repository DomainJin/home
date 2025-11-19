#define DELAY_TIME_MS 50
#define FREQ 20000000

unsigned char last_touch = 0;
unsigned char last_stable_touch = 0;


#define DEBOUNCE_MS 50 // th?i gian ch?ng d?i
unsigned int debounce_timer = 0;
unsigned char stable_touch = 0;   // tr?ng th?i ch?m d? du?c ch?ng d?i
unsigned char last_raw_touch = 0; // luu tr?ng th?i th? d? so s?nh thay d?i
unsigned int touch_value;
unsigned char raw_touch;

// Bi?n d? nh?n ngu?ng t? ESP32 - siêu t?i uu RAM
char uart_buffer[12];  // Gi?m t? 16 xu?ng 12 - v?a d? "THRESHOLD:999"
unsigned char uart_index = 0;
unsigned char uart_ready = 0;
unsigned char uart_counter = 0;  // B? d?m d? gi?m t?n su?t check UART
unsigned char calibrating = 0;   // C? b?o v? trong quá trình calibration
unsigned char calib_done = 0;    // C? dã calibration xong - b?o v? ngu?ng
unsigned char send_cycle = 0;    // Chu k? g?i d? li?u: 0-3=g?i, 4-5=nh?n

#define NUM_CALIB_SAMPLE 50
unsigned int NGUONG_CHAM = 0;
unsigned int delta = 100;
unsigned long total = 0;
unsigned int sample;
unsigned char txt_calib[12];
unsigned int avg;
unsigned int send_enabled;
void calib_touch_threshold() {
    unsigned char i;
    calibrating = 1;  // B?o v? trong quá trình calibration
    total = 0;        // Reset total tru?c khi calibration
    UART1_Write_Text("Calib start\r\n");
    for(i = 0; i < NUM_CALIB_SAMPLE; i++) {
    C1CH1_BIT=0;C1CH0_BIT=1;    C2CH1_BIT=0; C2CH0_BIT=1;
        Tmr1L=0;
       Tmr1H=0;
       delay_ms(DELAY_TIME_MS);
       sample=Tmr1L+tmr1H*255;
        total += sample;
        WordToStr(sample, txt_calib);
        UART1_Write_Text("Sample: ");
        UART1_Write_Text(txt_calib);
        UART1_Write_Text("\r\n");
    }
    // Debug: in total tru?c khi chia
    WordToStr(total, txt_calib);
    UART1_Write_Text("Total samples: ");
    UART1_Write_Text(txt_calib);
    UART1_Write_Text("\r\n");

    // S?a l?i tràn s? khi chia
    avg = (unsigned int)(total / NUM_CALIB_SAMPLE);

    // Debug: in average
    WordToStr(avg, txt_calib);
    UART1_Write_Text("Avg calculated: ");
    UART1_Write_Text(txt_calib);
    UART1_Write_Text("\r\n");

    // S?a công th?c: ngu?ng = avg + delta (không ph?i tr?)
    // Vì khi ch?m, giá tr? s? GI?M xu?ng du?i ngu?ng
    NGUONG_CHAM = avg - delta;

    WordToStr(NGUONG_CHAM, txt_calib);
    UART1_Write_Text("Final threshold: ");
    UART1_Write_Text(txt_calib);
    UART1_Write_Text("\r\n");
    calibrating = 0;  // K?t thúc calibration
    calib_done = 1;   // Ðánh d?u dã calibration - b?o v? ngu?ng
}

// Hàm x? lý d? li?u UART t? ESP32 - siêu t?i uu RAM
void process_uart_data() {
    if (UART1_Data_Ready()) {
        char ch = UART1_Read();

        if (ch == '\n') {
            uart_ready = 1;
        }
        else if (uart_index < 11) { // Gi?m t? 15 xu?ng 11 d? match buffer[12]
            uart_buffer[uart_index++] = ch;
        }
    }

    // X? lý khi nh?n xong d? li?u
    if (uart_ready) {
        uart_buffer[uart_index] = '\0';
        uart_ready = 0;

        // X? lý threshold - cho phép c?p nh?t t? ESP32 ngay c? sau calibration
        if (!calibrating) {
            // Ki?m tra format "THRESHOLD:xxxx" - t?i uu t?i da
            if (uart_index >= 10 &&
                uart_buffer[0] == 'T' && uart_buffer[1] == 'H' &&
                uart_buffer[2] == 'R' && uart_buffer[9] == ':') {

                unsigned int val = 0;
                unsigned char i = 10; // Sau d?u ':'

                // Convert s? - inline d? ti?t ki?m stack
                while (i < uart_index && uart_buffer[i] >= '0' && uart_buffer[i] <= '9') {
                    val = val * 10 + (uart_buffer[i] - '0');
                    i++;
                }

                // Validate và c?p nh?t - luôn cho phép override
                if (val > 100 && val < 5000) {
                    NGUONG_CHAM = val;
                    UART1_Write('T'); // Xác nh?n c?p nh?t thành công
                }
            }
        }

        uart_index = 0; // Reset
    }
}

int a1,a2,a3,a4,a11=0,a22=0,a33=0,a44=0,q1=1,q2=1,q3=1,q4=1,tam1=1,tam2=1,tam3=1,tam4=1;
int khoa1=0,khoa2=0,khoa3=0,khoa4=0;
int nguong=0;
char txt[7];




void main()
{
 trisd=0;
 portd=0;
 TRISC.B0 = 1;
 PORTC.B0 = 0;
 TRISA=0B11011111;

 ANSEL=0b11011111;


 ////////////////////////////////////////////////////mtouch/////////////
 CM1CON0=0B10010100; //BAT CAPARATOR,
                    //0
                    //KO XUAT RA CHAN C1OUT
                    //DAO NGO RA
                    //0
                    //NOI VAO VREF
                    //CHON KENH 0

VRCON=0B10101111;   //BAT REF
                    //NGAT KET NOI CHAN VREF
                    //BAT CHIA 24
                    //CHON V LA AP NGUON
                    //VREF=2/3VDD

SRCON=0B11110000;   //CHAN C2OUT GAN VAO CHAN Q BU
                    //CHAN C1OUT GAN VAO CHAN Q
                    //ENABLE NGO VAO CAPARATOR 1
                    //ENABLE NGO VAO CAPARATOR 2
                    //DISSABLE CHAN RESET HARDWARE
                    //0
                    //0

CM2CON0=0B10100000; //BAT CAPARATOR
                    //0
                    //KET NOI NGO RA VAO CHAN C2OUT
                    //KO DAO NGO RA
                    //0
                    //KOI NOI RA CHAN C2IN+
                    //CHON KENH 0

CM2CON1=0B00110010; //KHONG DAO
                    //KHONG DAO
                    //CHON CHAN VAO LA C1CREF
                    //CHON CHAN VAO LA C2VREF
                    //0
                    //0

T1CON=0B10100111;   //ENABLE CHO TIMER1
                    //EMABLE CHO TIMER1
                    //CHIA TAN   4
                    //CHIA TAN
                    //TAT DAO DONG LP
                    //KO CHON SYNCHRONIZE
                    //CHON NGUON XONG LA CHAN T1CKI\
                    //BAT TIMER1
delay_ms(500);

TRISB=0x00;
ANSELH=0x00;


TRISC.B6 = 0;

TRISC.B7 = 1;

UART1_Init(9600);

UART1_Write_Text("From Pic With Luv");
delay_ms(2000);
calib_touch_threshold();
delay_ms(2000);
 while(1)
 {
        // Chu k? g?i/nh?n xen k? d? tránh xung d?t UART
        send_cycle++;
        if (send_cycle > 5) send_cycle = 0;

        // Uu tiên nh?n l?nh t? ESP32 trong chu k? 4-5
        if (send_cycle >= 4) {
            // Th?i gian dành riêng cho nh?n - không g?i gì
            process_uart_data();
            delay_ms(DELAY_TIME_MS); // Ch? d? nh?n d? li?u
        }
        else {
            // Chu k? 0-3: Ðo và g?i d? li?u nhu bình thu?ng

            // Ðo giá tr? c?m ?ng
            C1CH1_BIT=0; C1CH0_BIT=1; C2CH1_BIT=0; C2CH0_BIT=1; // Kênh 0
            Tmr1L = 0;
            Tmr1H = 0;
            delay_ms(DELAY_TIME_MS);
            touch_value = Tmr1L + Tmr1H * 255;

            // Ch? g?i d? li?u trong chu k? 0-2 v?i format dúng cho ESP32
            if (send_cycle <= 2) {
                // G?i theo format: RawTouch:value\nThreshold:value\nvalue
                UART1_Write_Text("RawTouch:");
                WordToStr(raw_touch, txt);
                UART1_Write_Text(txt);
                UART1_Write_Text("\n");

                UART1_Write_Text("Threshold:");
                WordToStr(NGUONG_CHAM, txt);
                UART1_Write_Text(txt);
                UART1_Write_Text("\n");

                WordToStr(touch_value, txt);
                UART1_Write_Text(txt);
                UART1_Write_Text("\n");
            }

            // X? lý touch detection và debounce - luôn th?c hi?n
            raw_touch = (touch_value < NGUONG_CHAM) ? 1 : 0;

            if(raw_touch != last_raw_touch) {
                debounce_timer = 0;
                last_raw_touch = raw_touch;
            } else {
                debounce_timer += DELAY_TIME_MS;
                if(debounce_timer >= DEBOUNCE_MS) {
                    stable_touch = raw_touch;
                }
            }

            // Ch? g?i status khi có thay d?i v?i format dúng
            if (send_cycle <= 2) {
                if(stable_touch && !last_stable_touch) {
                    UART1_Write_Text("status\n1\n");
                }
                if(!stable_touch && last_stable_touch) {
                    UART1_Write_Text("status\n0\n");
                }
            }
            last_stable_touch = stable_touch;
        }
    }    // while


} // void