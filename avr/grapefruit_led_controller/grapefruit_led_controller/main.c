#include <atmel_start.h>
#include <string.h>

#include "my_i2c.h"
#include "led.h"



// things for twi (i2c) interface

// max message should be large enough to handle an entire array update
#define MAX_I2C_MESSAGE_LENGTH			(LED_ARRAY_BYTE_SIZE+1)
uint8_t rx_buffer[MAX_I2C_MESSAGE_LENGTH];
uint8_t rx_buffer_index = 0;

// led controller will not transmit anything
// uint8_t tx_buffer[MAX_I2C_MESSAGE_LENGTH];
// uint8_t tx_buffer_index = 0;

// TWI1 CALLBACKS
// THESE ARE TAKING PLACE IN THE ISR FOR TWI1
void twi1_read_byte_callback(uint8_t byte)
{
	rx_buffer[rx_buffer_index++] = byte;
	if (rx_buffer_index >= MAX_I2C_MESSAGE_LENGTH)
		rx_buffer_index = 0;
}

void twi1_read_complete_callback(uint8_t arg)
{
	// then reset buffer index to 0 so last message is overwritten
	rx_buffer_index = 0;
	
	// disect message and act on it
	switch (rx_buffer[0])
	{
		case LEDCMD_UPDATE_ALL:
		{
			memcpy(leds, &rx_buffer[1], LED_ARRAY_BYTE_SIZE);
			break;
		}
		
		case LEDCMD_UPDATE_SPECIFIC:
		{
			// rx_buffer[1] is the number of leds to update. see the spec
			for (uint8_t i = 0; i < rx_buffer[1]; i++)
			{
				uint8_t which_led = rx_buffer[i*4+2];
				leds[which_led].g = rx_buffer[which_led+1];
				leds[which_led].r = rx_buffer[which_led+2];
				leds[which_led].b = rx_buffer[which_led+3];
			}
			break;
		}
	}
	
	// we should likely update the leds at this point
	write_led_data((uint8_t*)leds, LED_ARRAY_BYTE_SIZE);
}

// callback for sending data in slave transmitter mode
// the return value should specify if there is more data to send (return 1)
// or if there is no more data to send (return 0)
uint8_t twi1_send_data_callback(uint8_t arg)
{
	/*
	// load byte to send and increment buffer index
	TWDR1 = tx_buffer[tx_buffer_index++];
	
	// if our index overflows the max number of bytes we can send, then we are done sending this message
	if (tx_buffer_index >= MAX_I2C_MESSAGE_LENGTH)
	{
		tx_buffer_index = 0;
		return 0;
	}
	
	return 1;
	*/
	
	TWDR1 = 0xFF;
	return 0;
}


/*
 *	INTERRUPT SERVICE ROUTINE FOR TIMER0
 *	this timer should be triggered about 30 times per second
 *	cpu frequency = 8Mhz / 1024 prescaler / 256 max value for timer0 = 30.5 interrupts/updates per second
 *	this routine will animate the leds and send out their new values across the data pin
 */
ISR (TIMER0_OVF_vect)
{
	// animate leds
	// send data out from portb0
	write_led_data((uint8_t*)leds, LED_ARRAY_BYTE_SIZE);
}



int main(void)
{
	/* Initializes MCU, drivers and middleware */
	atmel_start_init();
	
	twi1_slave_init(0x1a);
	
	DDRB |= (1 << PINB0);
	
	// zero out led array, turning all leds off
	memset(leds, 0x04, LED_ARRAY_BYTE_SIZE);
	// write data to leds
	write_led_data((uint8_t*)leds, LED_ARRAY_BYTE_SIZE);
	
	// interrupts not enabled by default, so enable them
	sei();
	
	/* Replace with your application code */
	while (1) 
	{
		
	}
}
