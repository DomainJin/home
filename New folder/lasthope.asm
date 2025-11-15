
_calib_touch_threshold:

;lasthope.c,23 :: 		void calib_touch_threshold() {
;lasthope.c,25 :: 		UART1_Write_Text("Calib start\r\n");
	MOVLW      ?lstr1_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,26 :: 		for(i = 0; i < NUM_CALIB_SAMPLE; i++) {
	CLRF       calib_touch_threshold_i_L0+0
L_calib_touch_threshold0:
	MOVLW      50
	SUBWF      calib_touch_threshold_i_L0+0, 0
	BTFSC      STATUS+0, 0
	GOTO       L_calib_touch_threshold1
;lasthope.c,27 :: 		C1CH1_BIT=0;C1CH0_BIT=1;    C2CH1_BIT=0; C2CH0_BIT=1;
	BCF        C1CH1_bit+0, BitPos(C1CH1_bit+0)
	BSF        C1CH0_bit+0, BitPos(C1CH0_bit+0)
	BCF        C2CH1_bit+0, BitPos(C2CH1_bit+0)
	BSF        C2CH0_bit+0, BitPos(C2CH0_bit+0)
;lasthope.c,28 :: 		Tmr1L=0;
	CLRF       TMR1L+0
;lasthope.c,29 :: 		Tmr1H=0;
	CLRF       TMR1H+0
;lasthope.c,30 :: 		delay_ms(DELAY_TIME_MS);
	MOVLW      2
	MOVWF      R11+0
	MOVLW      69
	MOVWF      R12+0
	MOVLW      169
	MOVWF      R13+0
L_calib_touch_threshold3:
	DECFSZ     R13+0, 1
	GOTO       L_calib_touch_threshold3
	DECFSZ     R12+0, 1
	GOTO       L_calib_touch_threshold3
	DECFSZ     R11+0, 1
	GOTO       L_calib_touch_threshold3
	NOP
	NOP
;lasthope.c,31 :: 		sample=Tmr1L+tmr1H*255;
	MOVF       TMR1H+0, 0
	MOVWF      R0+0
	MOVLW      255
	MOVWF      R4+0
	CALL       _Mul_8X8_U+0
	MOVF       R0+0, 0
	ADDWF      TMR1L+0, 0
	MOVWF      R4+0
	MOVLW      0
	BTFSC      STATUS+0, 0
	ADDLW      1
	ADDWF      R0+1, 0
	MOVWF      R4+1
	MOVF       R4+0, 0
	MOVWF      _sample+0
	MOVF       R4+1, 0
	MOVWF      _sample+1
;lasthope.c,32 :: 		total += sample;
	MOVF       R4+0, 0
	MOVWF      R0+0
	MOVF       R4+1, 0
	MOVWF      R0+1
	CLRF       R0+2
	CLRF       R0+3
	MOVF       _total+0, 0
	ADDWF      R0+0, 1
	MOVF       _total+1, 0
	BTFSC      STATUS+0, 0
	INCFSZ     _total+1, 0
	ADDWF      R0+1, 1
	MOVF       _total+2, 0
	BTFSC      STATUS+0, 0
	INCFSZ     _total+2, 0
	ADDWF      R0+2, 1
	MOVF       _total+3, 0
	BTFSC      STATUS+0, 0
	INCFSZ     _total+3, 0
	ADDWF      R0+3, 1
	MOVF       R0+0, 0
	MOVWF      _total+0
	MOVF       R0+1, 0
	MOVWF      _total+1
	MOVF       R0+2, 0
	MOVWF      _total+2
	MOVF       R0+3, 0
	MOVWF      _total+3
;lasthope.c,33 :: 		WordToStr(sample, txt_calib);
	MOVF       R4+0, 0
	MOVWF      FARG_WordToStr_input+0
	MOVF       R4+1, 0
	MOVWF      FARG_WordToStr_input+1
	MOVLW      _txt_calib+0
	MOVWF      FARG_WordToStr_output+0
	CALL       _WordToStr+0
;lasthope.c,34 :: 		UART1_Write_Text("Sample: ");
	MOVLW      ?lstr2_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,35 :: 		UART1_Write_Text(txt_calib);
	MOVLW      _txt_calib+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,36 :: 		UART1_Write_Text("\r\n");
	MOVLW      ?lstr3_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,26 :: 		for(i = 0; i < NUM_CALIB_SAMPLE; i++) {
	INCF       calib_touch_threshold_i_L0+0, 1
;lasthope.c,37 :: 		}
	GOTO       L_calib_touch_threshold0
L_calib_touch_threshold1:
;lasthope.c,38 :: 		WordToStr(total, txt_calib);
	MOVF       _total+0, 0
	MOVWF      FARG_WordToStr_input+0
	MOVF       _total+1, 0
	MOVWF      FARG_WordToStr_input+1
	MOVLW      _txt_calib+0
	MOVWF      FARG_WordToStr_output+0
	CALL       _WordToStr+0
;lasthope.c,39 :: 		UART1_Write_Text("Total: ");
	MOVLW      ?lstr4_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,40 :: 		UART1_Write_Text(total);
	MOVF       _total+0, 0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,41 :: 		UART1_Write_Text("\r\n");
	MOVLW      ?lstr5_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,42 :: 		avg = total / NUM_CALIB_SAMPLE;
	MOVLW      50
	MOVWF      R4+0
	CLRF       R4+1
	CLRF       R4+2
	CLRF       R4+3
	MOVF       _total+0, 0
	MOVWF      R0+0
	MOVF       _total+1, 0
	MOVWF      R0+1
	MOVF       _total+2, 0
	MOVWF      R0+2
	MOVF       _total+3, 0
	MOVWF      R0+3
	CALL       _Div_32x32_U+0
	MOVF       R0+0, 0
	MOVWF      _avg+0
	MOVF       R0+1, 0
	MOVWF      _avg+1
;lasthope.c,43 :: 		WordToStr(avg, txt_calib);
	MOVF       R0+0, 0
	MOVWF      FARG_WordToStr_input+0
	MOVF       R0+1, 0
	MOVWF      FARG_WordToStr_input+1
	MOVLW      _txt_calib+0
	MOVWF      FARG_WordToStr_output+0
	CALL       _WordToStr+0
;lasthope.c,44 :: 		UART1_Write_Text("Avg: ");
	MOVLW      ?lstr6_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,45 :: 		UART1_Write_Text(avg);
	MOVF       _avg+0, 0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,46 :: 		UART1_Write_Text("\r\n");
	MOVLW      ?lstr7_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,47 :: 		NGUONG_CHAM = avg - delta; // Tr? di 20%
	MOVF       _delta+0, 0
	SUBWF      _avg+0, 0
	MOVWF      R0+0
	MOVF       _delta+1, 0
	BTFSS      STATUS+0, 0
	ADDLW      1
	SUBWF      _avg+1, 0
	MOVWF      R0+1
	MOVF       R0+0, 0
	MOVWF      _NGUONG_CHAM+0
	MOVF       R0+1, 0
	MOVWF      _NGUONG_CHAM+1
;lasthope.c,48 :: 		WordToStr(NGUONG_CHAM, txt_calib);
	MOVF       R0+0, 0
	MOVWF      FARG_WordToStr_input+0
	MOVF       R0+1, 0
	MOVWF      FARG_WordToStr_input+1
	MOVLW      _txt_calib+0
	MOVWF      FARG_WordToStr_output+0
	CALL       _WordToStr+0
;lasthope.c,49 :: 		UART1_Write_Text("Calib threshold: ");
	MOVLW      ?lstr8_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,50 :: 		UART1_Write_Text(txt_calib);
	MOVLW      _txt_calib+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,51 :: 		UART1_Write_Text("\r\n");
	MOVLW      ?lstr9_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,52 :: 		}
L_end_calib_touch_threshold:
	RETURN
; end of _calib_touch_threshold

_main:

;lasthope.c,78 :: 		void main()
;lasthope.c,80 :: 		trisd=0;
	CLRF       TRISD+0
;lasthope.c,81 :: 		portd=0;
	CLRF       PORTD+0
;lasthope.c,82 :: 		TRISC.B0 = 1;
	BSF        TRISC+0, 0
;lasthope.c,83 :: 		PORTC.B0 = 0;
	BCF        PORTC+0, 0
;lasthope.c,84 :: 		TRISA=0B11011111;
	MOVLW      223
	MOVWF      TRISA+0
;lasthope.c,86 :: 		ANSEL=0b11011111;
	MOVLW      223
	MOVWF      ANSEL+0
;lasthope.c,90 :: 		CM1CON0=0B10010100; //BAT CAPARATOR,
	MOVLW      148
	MOVWF      CM1CON0+0
;lasthope.c,98 :: 		VRCON=0B10101111;   //BAT REF
	MOVLW      175
	MOVWF      VRCON+0
;lasthope.c,104 :: 		SRCON=0B11110000;   //CHAN C2OUT GAN VAO CHAN Q BU
	MOVLW      240
	MOVWF      SRCON+0
;lasthope.c,112 :: 		CM2CON0=0B10100000; //BAT CAPARATOR
	MOVLW      160
	MOVWF      CM2CON0+0
;lasthope.c,120 :: 		CM2CON1=0B00110010; //KHONG DAO
	MOVLW      50
	MOVWF      CM2CON1+0
;lasthope.c,127 :: 		T1CON=0B10100111;   //ENABLE CHO TIMER1
	MOVLW      167
	MOVWF      T1CON+0
;lasthope.c,135 :: 		delay_ms(500);
	MOVLW      13
	MOVWF      R11+0
	MOVLW      175
	MOVWF      R12+0
	MOVLW      182
	MOVWF      R13+0
L_main4:
	DECFSZ     R13+0, 1
	GOTO       L_main4
	DECFSZ     R12+0, 1
	GOTO       L_main4
	DECFSZ     R11+0, 1
	GOTO       L_main4
	NOP
;lasthope.c,137 :: 		TRISB=0x00;
	CLRF       TRISB+0
;lasthope.c,138 :: 		ANSELH=0x00;
	CLRF       ANSELH+0
;lasthope.c,139 :: 		Lcd_Init();
	CALL       _Lcd_Init+0
;lasthope.c,140 :: 		Lcd_Cmd(_LCD_TURN_ON);
	MOVLW      12
	MOVWF      FARG_Lcd_Cmd_out_char+0
	CALL       _Lcd_Cmd+0
;lasthope.c,141 :: 		Lcd_Cmd(_LCD_CURSOR_OFF);  // tat con tro
	MOVLW      12
	MOVWF      FARG_Lcd_Cmd_out_char+0
	CALL       _Lcd_Cmd+0
;lasthope.c,142 :: 		Lcd_Out(1, 1, "Nammo Nammo");
	MOVLW      1
	MOVWF      FARG_Lcd_Out_row+0
	MOVLW      1
	MOVWF      FARG_Lcd_Out_column+0
	MOVLW      ?lstr10_lasthope+0
	MOVWF      FARG_Lcd_Out_text+0
	CALL       _Lcd_Out+0
;lasthope.c,143 :: 		delay_ms(1000);
	MOVLW      26
	MOVWF      R11+0
	MOVLW      94
	MOVWF      R12+0
	MOVLW      110
	MOVWF      R13+0
L_main5:
	DECFSZ     R13+0, 1
	GOTO       L_main5
	DECFSZ     R12+0, 1
	GOTO       L_main5
	DECFSZ     R11+0, 1
	GOTO       L_main5
	NOP
;lasthope.c,144 :: 		lcd_cmd(_lcd_clear);
	MOVLW      1
	MOVWF      FARG_Lcd_Cmd_out_char+0
	CALL       _Lcd_Cmd+0
;lasthope.c,146 :: 		TRISC.B6 = 0;
	BCF        TRISC+0, 6
;lasthope.c,148 :: 		TRISC.B7 = 1;
	BSF        TRISC+0, 7
;lasthope.c,150 :: 		UART1_Init(9600);
	MOVLW      129
	MOVWF      SPBRG+0
	BSF        TXSTA+0, 2
	CALL       _UART1_Init+0
;lasthope.c,152 :: 		UART1_Write_Text("From Pic With Luv");
	MOVLW      ?lstr11_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,153 :: 		delay_ms(2000);
	MOVLW      51
	MOVWF      R11+0
	MOVLW      187
	MOVWF      R12+0
	MOVLW      223
	MOVWF      R13+0
L_main6:
	DECFSZ     R13+0, 1
	GOTO       L_main6
	DECFSZ     R12+0, 1
	GOTO       L_main6
	DECFSZ     R11+0, 1
	GOTO       L_main6
	NOP
	NOP
;lasthope.c,154 :: 		calib_touch_threshold();
	CALL       _calib_touch_threshold+0
;lasthope.c,155 :: 		delay_ms(2000);
	MOVLW      51
	MOVWF      R11+0
	MOVLW      187
	MOVWF      R12+0
	MOVLW      223
	MOVWF      R13+0
L_main7:
	DECFSZ     R13+0, 1
	GOTO       L_main7
	DECFSZ     R12+0, 1
	GOTO       L_main7
	DECFSZ     R11+0, 1
	GOTO       L_main7
	NOP
	NOP
;lasthope.c,156 :: 		while(1)
L_main8:
;lasthope.c,158 :: 		if (UART1_Data_Ready()) {
	CALL       _UART1_Data_Ready+0
	MOVF       R0+0, 0
	BTFSC      STATUS+0, 2
	GOTO       L_main10
;lasthope.c,159 :: 		char c = UART1_Read();
	CALL       _UART1_Read+0
	MOVF       R0+0, 0
	MOVWF      main_c_L2+0
;lasthope.c,162 :: 		if (c == '1') {
	MOVF       R0+0, 0
	XORLW      49
	BTFSS      STATUS+0, 2
	GOTO       L_main11
;lasthope.c,163 :: 		send_enabled = 1;
	MOVLW      1
	MOVWF      _send_enabled+0
	MOVLW      0
	MOVWF      _send_enabled+1
;lasthope.c,164 :: 		UART1_Write_Text("Send enabled\r\n");
	MOVLW      ?lstr12_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,166 :: 		}
	GOTO       L_main12
L_main11:
;lasthope.c,167 :: 		else if (c == '0') {
	MOVF       main_c_L2+0, 0
	XORLW      48
	BTFSS      STATUS+0, 2
	GOTO       L_main13
;lasthope.c,168 :: 		send_enabled = 0;
	CLRF       _send_enabled+0
	CLRF       _send_enabled+1
;lasthope.c,169 :: 		UART1_Write_Text("Send disabled\r\n");
	MOVLW      ?lstr13_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,171 :: 		}
L_main13:
L_main12:
;lasthope.c,172 :: 		}
L_main10:
;lasthope.c,175 :: 		C1CH1_BIT=0; C1CH0_BIT=1; C2CH1_BIT=0; C2CH0_BIT=1; // Kênh 0
	BCF        C1CH1_bit+0, BitPos(C1CH1_bit+0)
	BSF        C1CH0_bit+0, BitPos(C1CH0_bit+0)
	BCF        C2CH1_bit+0, BitPos(C2CH1_bit+0)
	BSF        C2CH0_bit+0, BitPos(C2CH0_bit+0)
;lasthope.c,176 :: 		Tmr1L = 0;
	CLRF       TMR1L+0
;lasthope.c,177 :: 		Tmr1H = 0;
	CLRF       TMR1H+0
;lasthope.c,178 :: 		delay_ms(DELAY_TIME_MS);
	MOVLW      2
	MOVWF      R11+0
	MOVLW      69
	MOVWF      R12+0
	MOVLW      169
	MOVWF      R13+0
L_main14:
	DECFSZ     R13+0, 1
	GOTO       L_main14
	DECFSZ     R12+0, 1
	GOTO       L_main14
	DECFSZ     R11+0, 1
	GOTO       L_main14
	NOP
	NOP
;lasthope.c,179 :: 		touch_value = Tmr1L + Tmr1H * 255;
	MOVF       TMR1H+0, 0
	MOVWF      R0+0
	MOVLW      255
	MOVWF      R4+0
	CALL       _Mul_8X8_U+0
	MOVF       R0+0, 0
	ADDWF      TMR1L+0, 0
	MOVWF      _touch_value+0
	MOVLW      0
	BTFSC      STATUS+0, 0
	ADDLW      1
	ADDWF      R0+1, 0
	MOVWF      _touch_value+1
;lasthope.c,182 :: 		if(send_enabled) {
	MOVF       _send_enabled+0, 0
	IORWF      _send_enabled+1, 0
	BTFSC      STATUS+0, 2
	GOTO       L_main15
;lasthope.c,183 :: 		WordToStr(touch_value, txt);
	MOVF       _touch_value+0, 0
	MOVWF      FARG_WordToStr_input+0
	MOVF       _touch_value+1, 0
	MOVWF      FARG_WordToStr_input+1
	MOVLW      _txt+0
	MOVWF      FARG_WordToStr_output+0
	CALL       _WordToStr+0
;lasthope.c,184 :: 		UART1_Write_Text("value\r\n");
	MOVLW      ?lstr14_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,185 :: 		UART1_Write_Text(txt);
	MOVLW      _txt+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,186 :: 		UART1_Write_Text("\r\n");
	MOVLW      ?lstr15_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,188 :: 		WordToStr(NGUONG_CHAM, txt);
	MOVF       _NGUONG_CHAM+0, 0
	MOVWF      FARG_WordToStr_input+0
	MOVF       _NGUONG_CHAM+1, 0
	MOVWF      FARG_WordToStr_input+1
	MOVLW      _txt+0
	MOVWF      FARG_WordToStr_output+0
	CALL       _WordToStr+0
;lasthope.c,189 :: 		UART1_Write_Text("threshold: ");
	MOVLW      ?lstr16_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,190 :: 		UART1_Write_Text(txt);
	MOVLW      _txt+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,191 :: 		UART1_Write_Text("\r\n");
	MOVLW      ?lstr17_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,192 :: 		WordToStr(raw_touch, txt);
	MOVF       _raw_touch+0, 0
	MOVWF      FARG_WordToStr_input+0
	CLRF       FARG_WordToStr_input+1
	MOVLW      _txt+0
	MOVWF      FARG_WordToStr_output+0
	CALL       _WordToStr+0
;lasthope.c,193 :: 		UART1_Write_Text("rawTouch: ");
	MOVLW      ?lstr18_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,194 :: 		UART1_Write_Text(txt);
	MOVLW      _txt+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,195 :: 		UART1_Write_Text("\r\n");
	MOVLW      ?lstr19_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,196 :: 		}
L_main15:
;lasthope.c,198 :: 		raw_touch = (touch_value < NGUONG_CHAM) ? 1 : 0; // tr?ng th?i c?m ?ng th?t s?
	MOVF       _NGUONG_CHAM+1, 0
	SUBWF      _touch_value+1, 0
	BTFSS      STATUS+0, 2
	GOTO       L__main31
	MOVF       _NGUONG_CHAM+0, 0
	SUBWF      _touch_value+0, 0
L__main31:
	BTFSC      STATUS+0, 0
	GOTO       L_main16
	MOVLW      1
	MOVWF      ?FLOC___mainT51+0
	GOTO       L_main17
L_main16:
	CLRF       ?FLOC___mainT51+0
L_main17:
	MOVF       ?FLOC___mainT51+0, 0
	MOVWF      _raw_touch+0
;lasthope.c,200 :: 		if(raw_touch != last_raw_touch) {
	MOVF       ?FLOC___mainT51+0, 0
	XORWF      _last_raw_touch+0, 0
	BTFSC      STATUS+0, 2
	GOTO       L_main18
;lasthope.c,202 :: 		debounce_timer = 0;
	CLRF       _debounce_timer+0
	CLRF       _debounce_timer+1
;lasthope.c,203 :: 		last_raw_touch = raw_touch;
	MOVF       _raw_touch+0, 0
	MOVWF      _last_raw_touch+0
;lasthope.c,204 :: 		} else {
	GOTO       L_main19
L_main18:
;lasthope.c,206 :: 		debounce_timer += DELAY_TIME_MS;
	MOVLW      50
	ADDWF      _debounce_timer+0, 0
	MOVWF      R1+0
	MOVF       _debounce_timer+1, 0
	BTFSC      STATUS+0, 0
	ADDLW      1
	MOVWF      R1+1
	MOVF       R1+0, 0
	MOVWF      _debounce_timer+0
	MOVF       R1+1, 0
	MOVWF      _debounce_timer+1
;lasthope.c,207 :: 		if(debounce_timer >= DEBOUNCE_MS) {
	MOVLW      0
	SUBWF      R1+1, 0
	BTFSS      STATUS+0, 2
	GOTO       L__main32
	MOVLW      50
	SUBWF      R1+0, 0
L__main32:
	BTFSS      STATUS+0, 0
	GOTO       L_main20
;lasthope.c,208 :: 		stable_touch = raw_touch; // ch? c?p nh?t khi d? th?i gian
	MOVF       _raw_touch+0, 0
	MOVWF      _stable_touch+0
;lasthope.c,209 :: 		}
L_main20:
;lasthope.c,210 :: 		}
L_main19:
;lasthope.c,214 :: 		if(stable_touch && !last_stable_touch) {
	MOVF       _stable_touch+0, 0
	BTFSC      STATUS+0, 2
	GOTO       L_main23
	MOVF       _last_stable_touch+0, 0
	BTFSS      STATUS+0, 2
	GOTO       L_main23
L__main28:
;lasthope.c,215 :: 		UART1_Write_Text("status\r\n");
	MOVLW      ?lstr20_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,216 :: 		UART1_Write('1');
	MOVLW      49
	MOVWF      FARG_UART1_Write_data_+0
	CALL       _UART1_Write+0
;lasthope.c,217 :: 		UART1_Write_Text("\r\n");
	MOVLW      ?lstr21_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,218 :: 		}
L_main23:
;lasthope.c,219 :: 		if(!stable_touch && last_stable_touch) {
	MOVF       _stable_touch+0, 0
	BTFSS      STATUS+0, 2
	GOTO       L_main26
	MOVF       _last_stable_touch+0, 0
	BTFSC      STATUS+0, 2
	GOTO       L_main26
L__main27:
;lasthope.c,220 :: 		UART1_Write_Text("status\r\n");
	MOVLW      ?lstr22_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,221 :: 		UART1_Write('0');
	MOVLW      48
	MOVWF      FARG_UART1_Write_data_+0
	CALL       _UART1_Write+0
;lasthope.c,222 :: 		UART1_Write_Text("\r\n");
	MOVLW      ?lstr23_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,223 :: 		}
L_main26:
;lasthope.c,224 :: 		last_stable_touch = stable_touch;
	MOVF       _stable_touch+0, 0
	MOVWF      _last_stable_touch+0
;lasthope.c,225 :: 		}    // while
	GOTO       L_main8
;lasthope.c,228 :: 		} // void
L_end_main:
	GOTO       $+0
; end of _main
