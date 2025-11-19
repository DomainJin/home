#line 1 "C:/Users/minhc/Desktop/VisionX/home/home/New folder/lasthope.c"



unsigned char last_touch = 0;
unsigned char last_stable_touch = 0;



unsigned int debounce_timer = 0;
unsigned char stable_touch = 0;
unsigned char last_raw_touch = 0;
unsigned int touch_value;
unsigned char raw_touch;


char uart_buffer[12];
unsigned char uart_index = 0;
unsigned char uart_ready = 0;
unsigned char uart_counter = 0;
unsigned char calibrating = 0;
unsigned char calib_done = 0;
unsigned char send_cycle = 0;


unsigned int NGUONG_CHAM = 0;
unsigned int delta = 100;
unsigned long total = 0;
unsigned int sample;
unsigned char txt_calib[12];
unsigned int avg;
unsigned int send_enabled;
void calib_touch_threshold() {
 unsigned char i;
 calibrating = 1;
 total = 0;
 UART1_Write_Text("Calib start\r\n");
 for(i = 0; i <  50 ; i++) {
 C1CH1_BIT=0;C1CH0_BIT=1; C2CH1_BIT=0; C2CH0_BIT=1;
 Tmr1L=0;
 Tmr1H=0;
 delay_ms( 50 );
 sample=Tmr1L+tmr1H*255;
 total += sample;
 WordToStr(sample, txt_calib);
 UART1_Write_Text("Sample: ");
 UART1_Write_Text(txt_calib);
 UART1_Write_Text("\r\n");
 }

 WordToStr(total, txt_calib);
 UART1_Write_Text("Total samples: ");
 UART1_Write_Text(txt_calib);
 UART1_Write_Text("\r\n");


 avg = (unsigned int)(total /  50 );


 WordToStr(avg, txt_calib);
 UART1_Write_Text("Avg calculated: ");
 UART1_Write_Text(txt_calib);
 UART1_Write_Text("\r\n");



 NGUONG_CHAM = avg - delta;

 WordToStr(NGUONG_CHAM, txt_calib);
 UART1_Write_Text("Final threshold: ");
 UART1_Write_Text(txt_calib);
 UART1_Write_Text("\r\n");
 calibrating = 0;
 calib_done = 1;
}


void process_uart_data() {
 if (UART1_Data_Ready()) {
 char ch = UART1_Read();

 if (ch == '\n') {
 uart_ready = 1;
 }
 else if (uart_index < 11) {
 uart_buffer[uart_index++] = ch;
 }
 }


 if (uart_ready) {
 uart_buffer[uart_index] = '\0';
 uart_ready = 0;


 if (!calibrating) {

 if (uart_index >= 10 &&
 uart_buffer[0] == 'T' && uart_buffer[1] == 'H' &&
 uart_buffer[2] == 'R' && uart_buffer[9] == ':') {

 unsigned int val = 0;
 unsigned char i = 10;


 while (i < uart_index && uart_buffer[i] >= '0' && uart_buffer[i] <= '9') {
 val = val * 10 + (uart_buffer[i] - '0');
 i++;
 }


 if (val > 100 && val < 5000) {
 NGUONG_CHAM = val;
 UART1_Write('T');
 }
 }
 }

 uart_index = 0;
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



 CM1CON0=0B10010100;







VRCON=0B10101111;





SRCON=0B11110000;







CM2CON0=0B10100000;







CM2CON1=0B00110010;






T1CON=0B10100111;
#line 187 "C:/Users/minhc/Desktop/VisionX/home/home/New folder/lasthope.c"
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

 send_cycle++;
 if (send_cycle > 5) send_cycle = 0;


 if (send_cycle >= 4) {

 process_uart_data();
 delay_ms( 50 );
 }
 else {



 C1CH1_BIT=0; C1CH0_BIT=1; C2CH1_BIT=0; C2CH0_BIT=1;
 Tmr1L = 0;
 Tmr1H = 0;
 delay_ms( 50 );
 touch_value = Tmr1L + Tmr1H * 255;


 if (send_cycle <= 2) {

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


 raw_touch = (touch_value < NGUONG_CHAM) ? 1 : 0;

 if(raw_touch != last_raw_touch) {
 debounce_timer = 0;
 last_raw_touch = raw_touch;
 } else {
 debounce_timer +=  50 ;
 if(debounce_timer >=  50 ) {
 stable_touch = raw_touch;
 }
 }


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
 }


}
