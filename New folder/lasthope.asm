
_calib_touch_threshold:

;lasthope.c,32 :: 		void calib_touch_threshold() {
;lasthope.c,34 :: 		calibrating = 1;  // B?o v? trong quá trình calibration
	MOVLW      1
	MOVWF      _calibrating+0
;lasthope.c,35 :: 		total = 0;        // Reset total tru?c khi calibration
	CLRF       _total+0
	CLRF       _total+1
	CLRF       _total+2
	CLRF       _total+3
;lasthope.c,36 :: 		UART1_Write_Text("Calib start\r\n");
	MOVLW      ?lstr1_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,37 :: 		for(i = 0; i < NUM_CALIB_SAMPLE; i++) {
	CLRF       calib_touch_threshold_i_L0+0
L_calib_touch_threshold0:
	MOVLW      50
	SUBWF      calib_touch_threshold_i_L0+0, 0
	BTFSC      STATUS+0, 0
	GOTO       L_calib_touch_threshold1
;lasthope.c,38 :: 		C1CH1_BIT=0;C1CH0_BIT=1;    C2CH1_BIT=0; C2CH0_BIT=1;
	BCF        C1CH1_bit+0, BitPos(C1CH1_bit+0)
	BSF        C1CH0_bit+0, BitPos(C1CH0_bit+0)
	BCF        C2CH1_bit+0, BitPos(C2CH1_bit+0)
	BSF        C2CH0_bit+0, BitPos(C2CH0_bit+0)
;lasthope.c,39 :: 		Tmr1L=0;
	CLRF       TMR1L+0
;lasthope.c,40 :: 		Tmr1H=0;
	CLRF       TMR1H+0
;lasthope.c,41 :: 		delay_ms(DELAY_TIME_MS);
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
;lasthope.c,42 :: 		sample=Tmr1L+tmr1H*255;
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
;lasthope.c,43 :: 		total += sample;
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
;lasthope.c,44 :: 		WordToStr(sample, txt_calib);
	MOVF       R4+0, 0
	MOVWF      FARG_WordToStr_input+0
	MOVF       R4+1, 0
	MOVWF      FARG_WordToStr_input+1
	MOVLW      _txt_calib+0
	MOVWF      FARG_WordToStr_output+0
	CALL       _WordToStr+0
;lasthope.c,45 :: 		UART1_Write_Text("Sample: ");
	MOVLW      ?lstr2_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,46 :: 		UART1_Write_Text(txt_calib);
	MOVLW      _txt_calib+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,47 :: 		UART1_Write_Text("\r\n");
	MOVLW      ?lstr3_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,37 :: 		for(i = 0; i < NUM_CALIB_SAMPLE; i++) {
	INCF       calib_touch_threshold_i_L0+0, 1
;lasthope.c,48 :: 		}
	GOTO       L_calib_touch_threshold0
L_calib_touch_threshold1:
;lasthope.c,50 :: 		WordToStr(total, txt_calib);
	MOVF       _total+0, 0
	MOVWF      FARG_WordToStr_input+0
	MOVF       _total+1, 0
	MOVWF      FARG_WordToStr_input+1
	MOVLW      _txt_calib+0
	MOVWF      FARG_WordToStr_output+0
	CALL       _WordToStr+0
;lasthope.c,51 :: 		UART1_Write_Text("Total samples: ");
	MOVLW      ?lstr4_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,52 :: 		UART1_Write_Text(txt_calib);
	MOVLW      _txt_calib+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,53 :: 		UART1_Write_Text("\r\n");
	MOVLW      ?lstr5_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,56 :: 		avg = (unsigned int)(total / NUM_CALIB_SAMPLE);
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
;lasthope.c,59 :: 		WordToStr(avg, txt_calib);
	MOVF       R0+0, 0
	MOVWF      FARG_WordToStr_input+0
	MOVF       R0+1, 0
	MOVWF      FARG_WordToStr_input+1
	MOVLW      _txt_calib+0
	MOVWF      FARG_WordToStr_output+0
	CALL       _WordToStr+0
;lasthope.c,60 :: 		UART1_Write_Text("Avg calculated: ");
	MOVLW      ?lstr6_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,61 :: 		UART1_Write_Text(txt_calib);
	MOVLW      _txt_calib+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,62 :: 		UART1_Write_Text("\r\n");
	MOVLW      ?lstr7_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,66 :: 		NGUONG_CHAM = avg - delta;
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
;lasthope.c,68 :: 		WordToStr(NGUONG_CHAM, txt_calib);
	MOVF       R0+0, 0
	MOVWF      FARG_WordToStr_input+0
	MOVF       R0+1, 0
	MOVWF      FARG_WordToStr_input+1
	MOVLW      _txt_calib+0
	MOVWF      FARG_WordToStr_output+0
	CALL       _WordToStr+0
;lasthope.c,69 :: 		UART1_Write_Text("Final threshold: ");
	MOVLW      ?lstr8_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,70 :: 		UART1_Write_Text(txt_calib);
	MOVLW      _txt_calib+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,71 :: 		UART1_Write_Text("\r\n");
	MOVLW      ?lstr9_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,72 :: 		calibrating = 0;  // K?t thúc calibration
	CLRF       _calibrating+0
;lasthope.c,73 :: 		calib_done = 1;   // Ðánh d?u dã calibration - b?o v? ngu?ng
	MOVLW      1
	MOVWF      _calib_done+0
;lasthope.c,74 :: 		}
L_end_calib_touch_threshold:
	RETURN
; end of _calib_touch_threshold

_process_uart_data:

;lasthope.c,77 :: 		void process_uart_data() {
;lasthope.c,78 :: 		if (UART1_Data_Ready()) {
	CALL       _UART1_Data_Ready+0
	MOVF       R0+0, 0
	BTFSC      STATUS+0, 2
	GOTO       L_process_uart_data4
;lasthope.c,79 :: 		char ch = UART1_Read();
	CALL       _UART1_Read+0
	MOVF       R0+0, 0
	MOVWF      process_uart_data_ch_L1+0
;lasthope.c,81 :: 		if (ch == '\n') {
	MOVF       R0+0, 0
	XORLW      10
	BTFSS      STATUS+0, 2
	GOTO       L_process_uart_data5
;lasthope.c,82 :: 		uart_ready = 1;
	MOVLW      1
	MOVWF      _uart_ready+0
;lasthope.c,83 :: 		}
	GOTO       L_process_uart_data6
L_process_uart_data5:
;lasthope.c,84 :: 		else if (uart_index < 11) { // Gi?m t? 15 xu?ng 11 d? match buffer[12]
	MOVLW      11
	SUBWF      _uart_index+0, 0
	BTFSC      STATUS+0, 0
	GOTO       L_process_uart_data7
;lasthope.c,85 :: 		uart_buffer[uart_index++] = ch;
	MOVF       _uart_index+0, 0
	ADDLW      _uart_buffer+0
	MOVWF      FSR
	MOVF       process_uart_data_ch_L1+0, 0
	MOVWF      INDF+0
	INCF       _uart_index+0, 1
;lasthope.c,86 :: 		}
L_process_uart_data7:
L_process_uart_data6:
;lasthope.c,87 :: 		}
L_process_uart_data4:
;lasthope.c,90 :: 		if (uart_ready) {
	MOVF       _uart_ready+0, 0
	BTFSC      STATUS+0, 2
	GOTO       L_process_uart_data8
;lasthope.c,91 :: 		uart_buffer[uart_index] = '\0';
	MOVF       _uart_index+0, 0
	ADDLW      _uart_buffer+0
	MOVWF      FSR
	CLRF       INDF+0
;lasthope.c,92 :: 		uart_ready = 0;
	CLRF       _uart_ready+0
;lasthope.c,95 :: 		if (!calibrating) {
	MOVF       _calibrating+0, 0
	BTFSS      STATUS+0, 2
	GOTO       L_process_uart_data9
;lasthope.c,98 :: 		uart_buffer[0] == 'T' && uart_buffer[1] == 'H' &&
	MOVLW      10
	SUBWF      _uart_index+0, 0
	BTFSS      STATUS+0, 0
	GOTO       L_process_uart_data12
	MOVF       _uart_buffer+0, 0
	XORLW      84
	BTFSS      STATUS+0, 2
	GOTO       L_process_uart_data12
	MOVF       _uart_buffer+1, 0
	XORLW      72
	BTFSS      STATUS+0, 2
	GOTO       L_process_uart_data12
;lasthope.c,99 :: 		uart_buffer[2] == 'R' && uart_buffer[9] == ':') {
	MOVF       _uart_buffer+2, 0
	XORLW      82
	BTFSS      STATUS+0, 2
	GOTO       L_process_uart_data12
	MOVF       _uart_buffer+9, 0
	XORLW      58
	BTFSS      STATUS+0, 2
	GOTO       L_process_uart_data12
L__process_uart_data45:
;lasthope.c,101 :: 		unsigned int val = 0;
	CLRF       process_uart_data_val_L3+0
	CLRF       process_uart_data_val_L3+1
	MOVLW      10
	MOVWF      process_uart_data_i_L3+0
;lasthope.c,105 :: 		while (i < uart_index && uart_buffer[i] >= '0' && uart_buffer[i] <= '9') {
L_process_uart_data13:
	MOVF       _uart_index+0, 0
	SUBWF      process_uart_data_i_L3+0, 0
	BTFSC      STATUS+0, 0
	GOTO       L_process_uart_data14
	MOVF       process_uart_data_i_L3+0, 0
	ADDLW      _uart_buffer+0
	MOVWF      FSR
	MOVLW      48
	SUBWF      INDF+0, 0
	BTFSS      STATUS+0, 0
	GOTO       L_process_uart_data14
	MOVF       process_uart_data_i_L3+0, 0
	ADDLW      _uart_buffer+0
	MOVWF      FSR
	MOVF       INDF+0, 0
	SUBLW      57
	BTFSS      STATUS+0, 0
	GOTO       L_process_uart_data14
L__process_uart_data44:
;lasthope.c,106 :: 		val = val * 10 + (uart_buffer[i] - '0');
	MOVF       process_uart_data_val_L3+0, 0
	MOVWF      R0+0
	MOVF       process_uart_data_val_L3+1, 0
	MOVWF      R0+1
	MOVLW      10
	MOVWF      R4+0
	MOVLW      0
	MOVWF      R4+1
	CALL       _Mul_16X16_U+0
	MOVF       process_uart_data_i_L3+0, 0
	ADDLW      _uart_buffer+0
	MOVWF      FSR
	MOVLW      48
	SUBWF      INDF+0, 0
	MOVWF      R2+0
	CLRF       R2+1
	BTFSS      STATUS+0, 0
	DECF       R2+1, 1
	MOVF       R2+0, 0
	ADDWF      R0+0, 0
	MOVWF      process_uart_data_val_L3+0
	MOVF       R0+1, 0
	BTFSC      STATUS+0, 0
	ADDLW      1
	ADDWF      R2+1, 0
	MOVWF      process_uart_data_val_L3+1
;lasthope.c,107 :: 		i++;
	INCF       process_uart_data_i_L3+0, 1
;lasthope.c,108 :: 		}
	GOTO       L_process_uart_data13
L_process_uart_data14:
;lasthope.c,111 :: 		if (val > 100 && val < 5000) {
	MOVF       process_uart_data_val_L3+1, 0
	SUBLW      0
	BTFSS      STATUS+0, 2
	GOTO       L__process_uart_data50
	MOVF       process_uart_data_val_L3+0, 0
	SUBLW      100
L__process_uart_data50:
	BTFSC      STATUS+0, 0
	GOTO       L_process_uart_data19
	MOVLW      19
	SUBWF      process_uart_data_val_L3+1, 0
	BTFSS      STATUS+0, 2
	GOTO       L__process_uart_data51
	MOVLW      136
	SUBWF      process_uart_data_val_L3+0, 0
L__process_uart_data51:
	BTFSC      STATUS+0, 0
	GOTO       L_process_uart_data19
L__process_uart_data43:
;lasthope.c,112 :: 		NGUONG_CHAM = val;
	MOVF       process_uart_data_val_L3+0, 0
	MOVWF      _NGUONG_CHAM+0
	MOVF       process_uart_data_val_L3+1, 0
	MOVWF      _NGUONG_CHAM+1
;lasthope.c,113 :: 		UART1_Write('T'); // Xác nh?n c?p nh?t thành công
	MOVLW      84
	MOVWF      FARG_UART1_Write_data_+0
	CALL       _UART1_Write+0
;lasthope.c,114 :: 		}
L_process_uart_data19:
;lasthope.c,115 :: 		}
L_process_uart_data12:
;lasthope.c,116 :: 		}
L_process_uart_data9:
;lasthope.c,118 :: 		uart_index = 0; // Reset
	CLRF       _uart_index+0
;lasthope.c,119 :: 		}
L_process_uart_data8:
;lasthope.c,120 :: 		}
L_end_process_uart_data:
	RETURN
; end of _process_uart_data

_main:

;lasthope.c,130 :: 		void main()
;lasthope.c,132 :: 		trisd=0;
	CLRF       TRISD+0
;lasthope.c,133 :: 		portd=0;
	CLRF       PORTD+0
;lasthope.c,134 :: 		TRISC.B0 = 1;
	BSF        TRISC+0, 0
;lasthope.c,135 :: 		PORTC.B0 = 0;
	BCF        PORTC+0, 0
;lasthope.c,136 :: 		TRISA=0B11011111;
	MOVLW      223
	MOVWF      TRISA+0
;lasthope.c,138 :: 		ANSEL=0b11011111;
	MOVLW      223
	MOVWF      ANSEL+0
;lasthope.c,142 :: 		CM1CON0=0B10010100; //BAT CAPARATOR,
	MOVLW      148
	MOVWF      CM1CON0+0
;lasthope.c,150 :: 		VRCON=0B10101111;   //BAT REF
	MOVLW      175
	MOVWF      VRCON+0
;lasthope.c,156 :: 		SRCON=0B11110000;   //CHAN C2OUT GAN VAO CHAN Q BU
	MOVLW      240
	MOVWF      SRCON+0
;lasthope.c,164 :: 		CM2CON0=0B10100000; //BAT CAPARATOR
	MOVLW      160
	MOVWF      CM2CON0+0
;lasthope.c,172 :: 		CM2CON1=0B00110010; //KHONG DAO
	MOVLW      50
	MOVWF      CM2CON1+0
;lasthope.c,179 :: 		T1CON=0B10100111;   //ENABLE CHO TIMER1
	MOVLW      167
	MOVWF      T1CON+0
;lasthope.c,187 :: 		delay_ms(500);
	MOVLW      13
	MOVWF      R11+0
	MOVLW      175
	MOVWF      R12+0
	MOVLW      182
	MOVWF      R13+0
L_main20:
	DECFSZ     R13+0, 1
	GOTO       L_main20
	DECFSZ     R12+0, 1
	GOTO       L_main20
	DECFSZ     R11+0, 1
	GOTO       L_main20
	NOP
;lasthope.c,189 :: 		TRISB=0x00;
	CLRF       TRISB+0
;lasthope.c,190 :: 		ANSELH=0x00;
	CLRF       ANSELH+0
;lasthope.c,193 :: 		TRISC.B6 = 0;
	BCF        TRISC+0, 6
;lasthope.c,195 :: 		TRISC.B7 = 1;
	BSF        TRISC+0, 7
;lasthope.c,197 :: 		UART1_Init(9600);
	MOVLW      129
	MOVWF      SPBRG+0
	BSF        TXSTA+0, 2
	CALL       _UART1_Init+0
;lasthope.c,199 :: 		UART1_Write_Text("From Pic With Luv");
	MOVLW      ?lstr10_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,200 :: 		delay_ms(2000);
	MOVLW      51
	MOVWF      R11+0
	MOVLW      187
	MOVWF      R12+0
	MOVLW      223
	MOVWF      R13+0
L_main21:
	DECFSZ     R13+0, 1
	GOTO       L_main21
	DECFSZ     R12+0, 1
	GOTO       L_main21
	DECFSZ     R11+0, 1
	GOTO       L_main21
	NOP
	NOP
;lasthope.c,201 :: 		calib_touch_threshold();
	CALL       _calib_touch_threshold+0
;lasthope.c,202 :: 		delay_ms(2000);
	MOVLW      51
	MOVWF      R11+0
	MOVLW      187
	MOVWF      R12+0
	MOVLW      223
	MOVWF      R13+0
L_main22:
	DECFSZ     R13+0, 1
	GOTO       L_main22
	DECFSZ     R12+0, 1
	GOTO       L_main22
	DECFSZ     R11+0, 1
	GOTO       L_main22
	NOP
	NOP
;lasthope.c,203 :: 		while(1)
L_main23:
;lasthope.c,206 :: 		send_cycle++;
	INCF       _send_cycle+0, 1
;lasthope.c,207 :: 		if (send_cycle > 5) send_cycle = 0;
	MOVF       _send_cycle+0, 0
	SUBLW      5
	BTFSC      STATUS+0, 0
	GOTO       L_main25
	CLRF       _send_cycle+0
L_main25:
;lasthope.c,210 :: 		if (send_cycle >= 4) {
	MOVLW      4
	SUBWF      _send_cycle+0, 0
	BTFSS      STATUS+0, 0
	GOTO       L_main26
;lasthope.c,212 :: 		process_uart_data();
	CALL       _process_uart_data+0
;lasthope.c,213 :: 		delay_ms(DELAY_TIME_MS); // Ch? d? nh?n d? li?u
	MOVLW      2
	MOVWF      R11+0
	MOVLW      69
	MOVWF      R12+0
	MOVLW      169
	MOVWF      R13+0
L_main27:
	DECFSZ     R13+0, 1
	GOTO       L_main27
	DECFSZ     R12+0, 1
	GOTO       L_main27
	DECFSZ     R11+0, 1
	GOTO       L_main27
	NOP
	NOP
;lasthope.c,214 :: 		}
	GOTO       L_main28
L_main26:
;lasthope.c,219 :: 		C1CH1_BIT=0; C1CH0_BIT=1; C2CH1_BIT=0; C2CH0_BIT=1; // Kênh 0
	BCF        C1CH1_bit+0, BitPos(C1CH1_bit+0)
	BSF        C1CH0_bit+0, BitPos(C1CH0_bit+0)
	BCF        C2CH1_bit+0, BitPos(C2CH1_bit+0)
	BSF        C2CH0_bit+0, BitPos(C2CH0_bit+0)
;lasthope.c,220 :: 		Tmr1L = 0;
	CLRF       TMR1L+0
;lasthope.c,221 :: 		Tmr1H = 0;
	CLRF       TMR1H+0
;lasthope.c,222 :: 		delay_ms(DELAY_TIME_MS);
	MOVLW      2
	MOVWF      R11+0
	MOVLW      69
	MOVWF      R12+0
	MOVLW      169
	MOVWF      R13+0
L_main29:
	DECFSZ     R13+0, 1
	GOTO       L_main29
	DECFSZ     R12+0, 1
	GOTO       L_main29
	DECFSZ     R11+0, 1
	GOTO       L_main29
	NOP
	NOP
;lasthope.c,223 :: 		touch_value = Tmr1L + Tmr1H * 255;
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
;lasthope.c,226 :: 		if (send_cycle <= 2) {
	MOVF       _send_cycle+0, 0
	SUBLW      2
	BTFSS      STATUS+0, 0
	GOTO       L_main30
;lasthope.c,228 :: 		UART1_Write_Text("RawTouch:");
	MOVLW      ?lstr11_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,229 :: 		WordToStr(raw_touch, txt);
	MOVF       _raw_touch+0, 0
	MOVWF      FARG_WordToStr_input+0
	CLRF       FARG_WordToStr_input+1
	MOVLW      _txt+0
	MOVWF      FARG_WordToStr_output+0
	CALL       _WordToStr+0
;lasthope.c,230 :: 		UART1_Write_Text(txt);
	MOVLW      _txt+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,231 :: 		UART1_Write_Text("\n");
	MOVLW      ?lstr12_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,233 :: 		UART1_Write_Text("Threshold:");
	MOVLW      ?lstr13_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,234 :: 		WordToStr(NGUONG_CHAM, txt);
	MOVF       _NGUONG_CHAM+0, 0
	MOVWF      FARG_WordToStr_input+0
	MOVF       _NGUONG_CHAM+1, 0
	MOVWF      FARG_WordToStr_input+1
	MOVLW      _txt+0
	MOVWF      FARG_WordToStr_output+0
	CALL       _WordToStr+0
;lasthope.c,235 :: 		UART1_Write_Text(txt);
	MOVLW      _txt+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,236 :: 		UART1_Write_Text("\n");
	MOVLW      ?lstr14_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,238 :: 		WordToStr(touch_value, txt);
	MOVF       _touch_value+0, 0
	MOVWF      FARG_WordToStr_input+0
	MOVF       _touch_value+1, 0
	MOVWF      FARG_WordToStr_input+1
	MOVLW      _txt+0
	MOVWF      FARG_WordToStr_output+0
	CALL       _WordToStr+0
;lasthope.c,239 :: 		UART1_Write_Text(txt);
	MOVLW      _txt+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,240 :: 		UART1_Write_Text("\n");
	MOVLW      ?lstr15_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,241 :: 		}
L_main30:
;lasthope.c,244 :: 		raw_touch = (touch_value < NGUONG_CHAM) ? 1 : 0;
	MOVF       _NGUONG_CHAM+1, 0
	SUBWF      _touch_value+1, 0
	BTFSS      STATUS+0, 2
	GOTO       L__main53
	MOVF       _NGUONG_CHAM+0, 0
	SUBWF      _touch_value+0, 0
L__main53:
	BTFSC      STATUS+0, 0
	GOTO       L_main31
	MOVLW      1
	MOVWF      ?FLOC___mainT95+0
	GOTO       L_main32
L_main31:
	CLRF       ?FLOC___mainT95+0
L_main32:
	MOVF       ?FLOC___mainT95+0, 0
	MOVWF      _raw_touch+0
;lasthope.c,246 :: 		if(raw_touch != last_raw_touch) {
	MOVF       ?FLOC___mainT95+0, 0
	XORWF      _last_raw_touch+0, 0
	BTFSC      STATUS+0, 2
	GOTO       L_main33
;lasthope.c,247 :: 		debounce_timer = 0;
	CLRF       _debounce_timer+0
	CLRF       _debounce_timer+1
;lasthope.c,248 :: 		last_raw_touch = raw_touch;
	MOVF       _raw_touch+0, 0
	MOVWF      _last_raw_touch+0
;lasthope.c,249 :: 		} else {
	GOTO       L_main34
L_main33:
;lasthope.c,250 :: 		debounce_timer += DELAY_TIME_MS;
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
;lasthope.c,251 :: 		if(debounce_timer >= DEBOUNCE_MS) {
	MOVLW      0
	SUBWF      R1+1, 0
	BTFSS      STATUS+0, 2
	GOTO       L__main54
	MOVLW      50
	SUBWF      R1+0, 0
L__main54:
	BTFSS      STATUS+0, 0
	GOTO       L_main35
;lasthope.c,252 :: 		stable_touch = raw_touch;
	MOVF       _raw_touch+0, 0
	MOVWF      _stable_touch+0
;lasthope.c,253 :: 		}
L_main35:
;lasthope.c,254 :: 		}
L_main34:
;lasthope.c,257 :: 		if (send_cycle <= 2) {
	MOVF       _send_cycle+0, 0
	SUBLW      2
	BTFSS      STATUS+0, 0
	GOTO       L_main36
;lasthope.c,258 :: 		if(stable_touch && !last_stable_touch) {
	MOVF       _stable_touch+0, 0
	BTFSC      STATUS+0, 2
	GOTO       L_main39
	MOVF       _last_stable_touch+0, 0
	BTFSS      STATUS+0, 2
	GOTO       L_main39
L__main47:
;lasthope.c,259 :: 		UART1_Write_Text("status\n1\n");
	MOVLW      ?lstr16_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,260 :: 		}
L_main39:
;lasthope.c,261 :: 		if(!stable_touch && last_stable_touch) {
	MOVF       _stable_touch+0, 0
	BTFSS      STATUS+0, 2
	GOTO       L_main42
	MOVF       _last_stable_touch+0, 0
	BTFSC      STATUS+0, 2
	GOTO       L_main42
L__main46:
;lasthope.c,262 :: 		UART1_Write_Text("status\n0\n");
	MOVLW      ?lstr17_lasthope+0
	MOVWF      FARG_UART1_Write_Text_uart_text+0
	CALL       _UART1_Write_Text+0
;lasthope.c,263 :: 		}
L_main42:
;lasthope.c,264 :: 		}
L_main36:
;lasthope.c,265 :: 		last_stable_touch = stable_touch;
	MOVF       _stable_touch+0, 0
	MOVWF      _last_stable_touch+0
;lasthope.c,266 :: 		}
L_main28:
;lasthope.c,267 :: 		}    // while
	GOTO       L_main23
;lasthope.c,270 :: 		} // void
L_end_main:
	GOTO       $+0
; end of _main
