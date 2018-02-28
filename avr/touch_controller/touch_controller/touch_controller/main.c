#include <atmel_start.h>

#include <util/twi.h>
#include "my_i2c.h"


// things for twi interface
#define MAX_RECIEVE_BUFFER			16

uint8_t rx_buffer[MAX_RECIEVE_BUFFER];
uint8_t rx_buffer_index = 0;

#define MAX_SEND_BUFFER				2
uint8_t key_states[MAX_SEND_BUFFER];
uint8_t tx_buffer_index = 0;


// TWI1 CALLBACKS
void twi1_read_byte_callback(uint8_t byte)
{
	rx_buffer[rx_buffer_index++] = byte;
	if (rx_buffer_index >= MAX_RECIEVE_BUFFER)
		rx_buffer_index = 0;
}

void twi1_read_complete_callback(uint8_t arg)
{
	// here we should disect the message and act on it
	
	// then reset buffer index to 0 so last message is overwritten
	rx_buffer_index = 0;
}

// callback for sending data in slave transmitter mode
// the return value should specify if there is more data to send (return 1)
// or if there is no more data to send (return 0)
uint8_t twi1_send_data_callback(uint8_t arg)
{
	// load byte to send and increment buffer index
	TWDR1 = key_states[tx_buffer_index++];
	
	// if our index overflows the max number of bytes we can send, then we are done sending this message
	if (tx_buffer_index >= MAX_SEND_BUFFER)
	{
		tx_buffer_index = 0;
		return 0;
	}
	
	return 1;
}


extern volatile uint8_t measurement_done_touch;
uint8_t key_status = 0;

void update_touch_status(void);


int main(void)
{
	/* Initializes MCU, drivers and middleware */
	atmel_start_init();

	// enable interrupts
	sei();

	/* Replace with your application code */
	while (1) {
		touch_process();
		if (measurement_done_touch == 1) {
			update_touch_status();
		}
	}
}


void update_touch_status(void)
{
	key_status = get_sensor_state(0) & 0x80;
	if (0u != key_status) {
		key_states[0] |= (1 << 0);
	} else {
		key_states[0] &= ~(1 << 0);
	}
	key_status = get_sensor_state(1) & 0x80;
	if (0u != key_status) {
		key_states[0] |= (1 << 1);
		} else {
		key_states[0] &= ~(1 << 1);
	}
	key_status = get_sensor_state(2) & 0x80;
	if (0u != key_status) {
		key_states[0] |= (1 << 2);
		} else {
		key_states[0] &= ~(1 << 2);
	}
	key_status = get_sensor_state(3) & 0x80;
	if (0u != key_status) {
		key_states[0] |= (1 << 3);
		} else {
		key_states[0] &= ~(1 << 3);
	}
	key_status = get_sensor_state(4) & 0x80;
	if (0u != key_status) {
		key_states[0] |= (1 << 4);
		} else {
		key_states[0] &= ~(1 << 4);
	}
	key_status = get_sensor_state(5) & 0x80;
	if (0u != key_status) {
		key_states[0] |= (1 << 5);
		} else {
		key_states[0] &= ~(1 << 5);
	}
	key_status = get_sensor_state(6) & 0x80;
	if (0u != key_status) {
		key_states[0] |= (1 << 6);
		} else {
		key_states[0] &= ~(1 << 6);
	}
	key_status = get_sensor_state(7) & 0x80;
	if (0u != key_status) {
		key_states[0] |= (1 << 7);
		} else {
		key_states[0] &= ~(1 << 7);
	}
	key_status = get_sensor_state(8) & 0x80;
	if (0u != key_status) {
		key_states[1] |= (1 << 0);
		} else {
		key_states[1] &= ~(1 << 0);
	}
	key_status = get_sensor_state(9) & 0x80;
	if (0u != key_status) {
		key_states[1] |= (1 << 1);
		} else {
		key_states[1] &= ~(1 << 1);
	}
	key_status = get_sensor_state(10) & 0x80;
	if (0u != key_status) {
		key_states[1] |= (1 << 2);
		} else {
		key_states[1] &= ~(1 << 2);
	}
	key_status = get_sensor_state(11) & 0x80;
	if (0u != key_status) {
		key_states[1] |= (1 << 3);
		} else {
		key_states[1] &= ~(1 << 3);
	}
	key_status = get_sensor_state(12) & 0x80;
	if (0u != key_status) {
		key_states[1] |= (1 << 4);
		} else {
		key_states[1] &= ~(1 << 4);
	}
	key_status = get_sensor_state(13) & 0x80;
	if (0u != key_status) {
		key_states[1] |= (1 << 5);
		} else {
		key_states[1] &= ~(1 << 5);
	}
	key_status = get_sensor_state(14) & 0x80;
	if (0u != key_status) {
		key_states[1] |= (1 << 6);
		} else {
		key_states[1] &= ~(1 << 6);
	}
	key_status = get_sensor_state(15) & 0x80;
	if (0u != key_status) {
		key_states[1] |= (1 << 7);
		} else {
		key_states[1] &= ~(1 << 7);
	}
}
