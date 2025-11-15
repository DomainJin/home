#line 1 "C:/Users/SGM/Desktop/New folder/lasthope.c"



unsigned char last_touch = 0;
unsigned char last_stable_touch = 0;



unsigned int debounce_timer = 0;
unsigned char stable_touch = 0;
unsigned char last_raw_touch = 0;
unsigned int touch_value;
unsigned char raw_touch;


unsigned int NGUONG_CHAM = 0;
unsigned int delta = 100;
unsigned long total = 0;
unsigned int sample;
unsigned char txt_calib[12];
unsigned int avg;
unsigned int send_enabled;
void calib_touch_threshold() {
 unsigned char i;
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
 UART1_Write_Text("Total: ");
 UART1_Write_Text(total);
 UART1_Write_Text("\r\n");
 avg = total /  50 ;
 WordToStr(avg, txt_calib);
 UART1_Write_Text("Avg: ");
 UART1_Write_Text(avg);
 UART1_Write_Text("\r\n");
 NGUONG_CHAM = avg - delta;
 WordToStr(NGUONG_CHAM, txt_calib);
 UART1_Write_Text("Calib threshold: ");
 UART1_Write_Text(txt_calib);
 UART1_Write_Text("\r\n");
}

int a1,a2,a3,a4,a11=0,a22=0,a33=0,a44=0,q1=1,q2=1,q3=1,q4=1,tam1=1,tam2=1,tam3=1,tam4=1;
int khoa1=0,khoa2=0,khoa3=0,khoa4=0;
int nguong=0;
char txt[7];




sbit LCD_RS at RB4_bit;
sbit LCD_EN at RB5_bit;
sbit LCD_D4 at RB0_bit;
sbit LCD_D5 at RB1_bit;
sbit LCD_D6 at RB2_bit;
sbit LCD_D7 at RB3_bit;

sbit LCD_RS_Direction at TRISB4_bit;
sbit LCD_EN_Direction at TRISB5_bit;
sbit LCD_D4_Direction at TRISB0_bit;
sbit LCD_D5_Direction at TRISB1_bit;
sbit LCD_D6_Direction at TRISB2_bit;
sbit LCD_D7_Direction at TRISB3_bit;



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
#line 135 "C:/Users/SGM/Desktop/New folder/lasthope.c"
delay_ms(500);

TRISB=0x00;
ANSELH=0x00;
Lcd_Init();
Lcd_Cmd(_LCD_TURN_ON);
Lcd_Cmd(_LCD_CURSOR_OFF);
Lcd_Out(1, 1, "Nammo Nammo");
delay_ms(1000);
lcd_cmd(_lcd_clear);

TRISC.B6 = 0;

TRISC.B7 = 1;

UART1_Init(9600);

UART1_Write_Text("From Pic With Luv");
delay_ms(2000);
calib_touch_threshold();
delay_ms(2000);
 while(1)
 {
 if (UART1_Data_Ready()) {
 char c = UART1_Read();


 if (c == '1') {
 send_enabled = 1;
 UART1_Write_Text("Send enabled\r\n");

 }
 else if (c == '0') {
 send_enabled = 0;
 UART1_Write_Text("Send disabled\r\n");

 }
 }


 C1CH1_BIT=0; C1CH0_BIT=1; C2CH1_BIT=0; C2CH0_BIT=1;
 Tmr1L = 0;
 Tmr1H = 0;
 delay_ms( 50 );
 touch_value = Tmr1L + Tmr1H * 255;


 if(send_enabled) {
 WordToStr(touch_value, txt);
 UART1_Write_Text("value\r\n");
 UART1_Write_Text(txt);
 UART1_Write_Text("\r\n");

 WordToStr(NGUONG_CHAM, txt);
 UART1_Write_Text("threshold: ");
 UART1_Write_Text(txt);
 UART1_Write_Text("\r\n");
 WordToStr(raw_touch, txt);
 UART1_Write_Text("rawTouch: ");
 UART1_Write_Text(txt);
 UART1_Write_Text("\r\n");
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



 if(stable_touch && !last_stable_touch) {
 UART1_Write_Text("status\r\n");
 UART1_Write('1');
 UART1_Write_Text("\r\n");
 }
 if(!stable_touch && last_stable_touch) {
 UART1_Write_Text("status\r\n");
 UART1_Write('0');
 UART1_Write_Text("\r\n");
 }
 last_stable_touch = stable_touch;
 }


}
