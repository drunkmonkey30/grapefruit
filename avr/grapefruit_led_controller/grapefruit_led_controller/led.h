
#ifndef LED_H_
#define LED_H_

// forward declaration for asm function
void write_led_data(uint8_t*, uint8_t);

// our data structure for holding data sent to leds
typedef struct _RGB_tag
{
	uint8_t g;	// our leds want green first, then red
	uint8_t r;
	uint8_t b;
} RGB;

#define NUM_LEDS				(64)
#define BYTES_PER_LED			(sizeof(RGB))
#define LED_ARRAY_BYTE_SIZE		(NUM_LEDS*BYTES_PER_LED)

// the led array
RGB leds[NUM_LEDS];

// i2c message commands
#define LEDCMD_UPDATE_ALL		0x01
#define LEDCMD_UPDATE_SPECIFIC	0x02

#endif /* LED_H_ */