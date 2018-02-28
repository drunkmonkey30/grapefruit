
.include "../utils/assembler.h"

.global write_led_data

#define PORTB (0x05)// + 0x20)

; use like so:
; write_led_data((uint8_t*)leds, LED_ARRAY_BYTE_SIZE);
; leds is array of grb data, and its corresponding size in bytes

write_led_data:
		 movw   r26, r24      ;r26:27 = X = p_buf
         mov   r24, r22      ;r24:25 = count
         cli                  ;no interrupts from here on, we're cycle-counting
         in     r20, PORTB
         ori    r20, (1 << 0)         ;our '1' output
         in     r21, PORTB
         andi   r21, ~(1 << 0)        ;our '0' output
         ldi    r19, 7        ;7 bit counter (8th bit is different)
         ld     r18,X+        ;get first data byte

	loop1:
         out    PORTB, r20    ; 1   +0 start of a bit pulse
         lsl    r18           ; 1   +1 next bit into C, MSB first
         brcs   L1            ; 1/2 +2 branch if 1
         out    PORTB, r21    ; 1   +3 end hi for '0' bit (3 clocks hi)
         nop                  ; 1   +4
         bst    r18, 7        ; 1   +5 save last bit of data for fast branching
         subi   r19, 1        ; 1   +6 how many more bits for this byte?
         breq   bit8          ; 1/2 +7 last bit, do differently
         rjmp   loop1         ; 2   +8, 10 total for 0 bit
	L1:
         nop                  ; 1   +4
         bst    r18, 7        ; 1   +5 save last bit of data for fast branching
         subi   r19, 1        ; 1   +6 how many more bits for this byte
         out    PORTB, r21    ; 1   +7 end hi for '1' bit (7 clocks hi)
         brne   loop1         ; 2/1 +8 10 total for 1 bit (fall thru if last bit)
	bit8:
         ldi    r19, 7        ; 1   +9 bit count for next byte
         out    PORTB, r20    ; 1   +0 start of a bit pulse
         brts   L2            ; 1/2 +1 branch if last bit is a 1
         nop                  ; 1   +2
         out    PORTB, r21    ; 1   +3 end hi for '0' bit (3 clocks hi)
         ld     r18, X+       ; 2   +4 fetch next byte
         sbiw   r24, 1        ; 2   +6 dec byte counter
         brne   loop1         ; 2   +8 loop back or return
         ret
	L2:
         ld     r18, X+       ; 2   +3 fetch next byte
         sbiw   r24, 1        ; 2   +5 dec byte counter
         out     PORTB, r21   ; 1   +7 end hi for '1' bit (7 clocks hi)
         brne   loop1         ; 2   +8 loop back or return
         ret