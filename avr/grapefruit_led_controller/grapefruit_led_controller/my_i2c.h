/*
 * my_i2c.h
 *
 * Created: 1/1/2018 7:50:43 PM
 *  Author: dm
 */ 


#ifndef MY_I2C_H_
#define MY_I2C_H_

#include <avr/io.h>

/*

The Power Reduction TWI bit in the Power Reduction Register (PRRn.PRTWI) must be written to '0' to
enable the two-wire Serial Interface.

TWI0 is in PRR0, and TWI1 is in PRR1.


### THINGS TO DO IN MAIN PROGRAM

// things for twi interface
#define MAX_I2C_MESSAGE_LENGTH			32

uint8_t rx_buffer[MAX_I2C_MESSAGE_LENGTH];
uint8_t rx_buffer_index = 0;

uint8_t tx_buffer[MAX_I2C_MESSAGE_LENGTH];
uint8_t tx_buffer_index = 0;

// TWI1 CALLBACKS
void twi1_read_byte_callback(uint8_t byte)
{
	rx_buffer[rx_buffer_index++] = byte;
	if (rx_buffer_index >= MAX_I2C_MESSAGE_LENGTH)
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
	TWDR1 = tx_buffer[tx_buffer_index++];
	
	// if our index overflows the max number of bytes we can send, then we are done sending this message
	if (tx_buffer_index >= MAX_I2C_MESSAGE_LENGTH)
	{
		tx_buffer_index = 0;
		return 0;
	}
	
	return 1;
}

*/

#define TWI_NO_ACTION				0x00
#define TWI_RECEIVING_DATA			0x01
#define TWI_TRANSMITTING_DATA		0x02

#define TWI_RECEIVED_DATA			0x10
#define TWI_RECEIVED_STOP			0x20


// using twi 1
#define TWSR	TWSR1

void twi1_slave_init(uint8_t address);
void twi1_slave_start();
//uint8_t twi1_poll();

#endif /* MY_I2C_H_ */