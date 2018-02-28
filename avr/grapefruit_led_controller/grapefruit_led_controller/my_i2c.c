/*
 * my_i2c.c
 *
 * Created: 1/1/2018 7:50:57 PM
 *  Author: dm
 */ 


#include "my_i2c.h"
#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/twi.h>
#include <string.h>



/*
	CALLBACKS
	TO BE DEFINED BY THE MAIN PROGRAMS
*/
void twi1_read_byte_callback(uint8_t byte);
void twi1_read_complete_callback(uint8_t argument);
uint8_t twi1_send_data_callback(uint8_t argument);


inline void twi1_slave_init(uint8_t address)
{
	//To initiate the SR mode, the TWI (Slave) Address Register n (TWARn) and the TWI Control Register n
	//(TWCRn) must be initialized as follows:
	//The upper seven bits of TWARn are the address to which the 2-wire Serial Interface will respond when
	//addressed by a Master (TWARn.TWA[6:0]). If the LSB of TWARn is written to TWARn.TWGCI=1, the TWI
	//n will respond to the general call address (0x00), otherwise it will ignore the general call address.
	//TWCRn must hold a value of the type TWCRn=0100010x - TWCRn.TWEN must be written to '1' to
	//enable the TWI. TWCRn.TWEA bit must be written to '1' to enable the acknowledgment of the device’s
	//own slave address or the general call address. TWCRn.TWSTA and TWSTO must be written to zero.

	cli();

	PRR1 &= ~(1 << PRTWI1);
	
	// setup port e for sda and scl
	//DDRE |= (1 << PINE1) | (1 << PINE0);
	//PORTE &= ~((1 << PINE1) | (1 << PINE0));
	
	/* SCL bitrate = F_CPU / (16 + 2 * TWBR1 * TWPS value) */
	/* Configured bit rate is 100.000kHz, based on CPU frequency 8.000MHz */
	//TWBR1 = 0x20;          /* SCL bit rate: 100.000kHZ before prescaling */
	//TWSR1 = 0x00 << TWPS0; /* SCL precaler: 1, effective bitrate = 100.000kHz */

	// Set own TWI slave address, respond to general call
	TWAR1 = (address << 1) | 0x00;
	twi1_slave_start();
}

inline void twi1_slave_start()
{
	TWCR1 = (1<<TWEN1)|						// Enable TWI-interface and release TWI pins.
		(1<<TWIE)|(1<<TWINT)|				// clear interrupt flag, enable interface
		(1<<TWEA)|(0<<TWSTA)|(0<<TWSTO)|
		(0<<TWWC);
		
	sei();
}

uint8_t twi1_last_action = TWI_NO_ACTION;
ISR(TWI1_vect)
{
	uint8_t status = TW_STATUS;
	switch (status)
	{
		case (TW_SR_SLA_ACK):
		case (TW_SR_DATA_ACK):
		case (TW_SR_DATA_NACK):
			// skip over the first byte sent
			if (twi1_last_action == TWI_RECEIVING_DATA)
			twi1_read_byte_callback(TWDR1);
		
			TWCR1 = (1 << TWEN1) | (1 << TWIE1) | (1 << TWINT1) | (1 << TWEA1);
			twi1_last_action = TWI_RECEIVING_DATA;
		break;
		
		// A STOP condition or repeated START condition has been received while still addressed as Slave
		// Repeated START enables the Master to switch between Slaves, Master Transmitter
		// mode and Master Receiver mode without losing control over the bus.
		case (TW_SR_STOP):
			// if we were last recieving data and we got the stop message
			// then call the received data callback
			if (twi1_last_action == TWI_RECEIVING_DATA)
			{
				twi1_read_complete_callback(0);
			}
		
			//Switched to the not addressed Slave mode; own SLA will be recognized; GCA will be recognized if TWGCE = “1”
			TWCR1 = (1 << TWEN1) | (1 << TWIE1) | (1 << TWINT1) | (1 << TWEA1);
			twi1_last_action = TWI_NO_ACTION;
		break;
		
		case (TW_ST_SLA_ACK):
			// Got read command from master, need to enter slave transmit mode
			twi1_last_action = TWI_TRANSMITTING_DATA;
			
			// we should load a data byte to TWDR
			// do this by calling the callback defined by the application
			// check the return value to see if there is more data to send
			if (twi1_send_data_callback(0))
			{
				// there is more data to send, next state should be TW_ST_DATA_ACK
				TWCR1 = (1 << TWEN1) | (1 << TWIE1) | (1 << TWINT1) | (1 << TWEA1);
			}
			else
			{
				// there is no more data to send
				// Last data byte will be transmitted and NOT ACK should be received
				// next state should be 0xc0 (TW_ST_DATA_NACK)
				TWCR1 = (1 << TWEN1) | (1 << TWIE1) | (1 << TWINT1) | (0 << TWEA1);
			}
			
			// then clear the interrupt flag by writing 1 to it and enabling twi interface
			//TWCR1 = (1 << TWEN1) | (1 << TWIE1) | (1 << TWINT1) | (1 << TWEA1);
		break;
		
		case TW_ST_DATA_NACK:
			twi1_last_action = TWI_NO_ACTION;
			// the last data byte was sent and not ack was received
			// switch out of slave transmitter mode
			TWCR1 = (1 << TWEN1) | (1 << TWIE1) | (1 << TWINT1) | (1 << TWEA1) | (0 << TWSTA) | (0 << TWSTO);
		break;
		
		case TW_ST_DATA_ACK:
			// continue sending data
			if (twi1_send_data_callback(0))
			{
				// there is more data to send, next state should be TW_ST_DATA_ACK
				TWCR1 = (1 << TWEN1) | (1 << TWIE1) | (1 << TWINT1) | (1 << TWEA1);
			}
			else
			{
				// there is no more data to send
				// Last data byte will be transmitted and NOT ACK should be received
				// next state should be 0xc0 (TW_ST_DATA_NACK)
				TWCR1 = (1 << TWEN1) | (1 << TWIE1) | (1 << TWINT1) | (0 << TWEA1);
			}
		break;
		
		case TW_ST_LAST_DATA:
			TWCR1 = (1 << TWEN1) | (1 << TWIE1) | (1 << TWINT1) | (1 << TWEA1) | (0 << TWSTA) | (0 << TWSTO);
		break;
		
		case (TW_SR_ARB_LOST_SLA_ACK):
		case (TW_SR_GCALL_ACK):
		case (TW_SR_ARB_LOST_GCALL_ACK):
		case (TW_SR_GCALL_DATA_ACK):
		case (TW_SR_GCALL_DATA_NACK):
		case (TW_BUS_ERROR):
			TWCR1 = (1 << TWINT1) | (1 << TWSTO);
		
		default:
			twi1_last_action = TWI_NO_ACTION;
			// debugging point to check status register
			TWCR1 = (1 << TWEN1) | (1 << TWIE1) | (1 << TWINT1) | (1 << TWEA1);
	}
}


/*
	THIS IS HERE FOR DEBUGGING PURPOSES
	The documentation is not clear on which ISR is used for which interface
	for twi1_vect the headers say it is used when a transmission is complete
	I don't know if this is in general, or if the interrupt is specific to an interface
	it is likely specific, but it is here just in case.
	if this is ever called it should hit a breakpoint
	but it does not say anything about twi0_vect
*/
ISR(TWI0_vect)
{
	uint8_t status = TW_STATUS;
	switch (status)
	{
		default:
			// debugging point to check status register
			TWCR1 = (1 << TWEN1) | (1 << TWIE1) | (1 << TWINT1) | (1 << TWEA1);
	}
}

/* NOT USED
uint8_t twi1_poll()
{
	//When the TWI has finished an operation and expects application response, the TWINT Flag is set.
	while (!(TWCR1 & (1 << TWINT1)));

	uint8_t status = TW_STATUS;
	switch (status)
	{
		case (TW_SR_SLA_ACK):
		case (TW_SR_DATA_ACK):
		case (TW_SR_DATA_NACK):
			// skip over the first byte sent
			if (last_action == TWI_RECEIVING_DATA)
				twi1_read_byte_callback(TWDR1);
				
			TWCR1 = (1 << TWEN1) | (1 << TWIE1) | (1 << TWINT1) | (1 << TWEA1);
			last_action = TWI_RECEIVING_DATA;
			
			return TWI_RECEIVED_DATA;
		break;
		
		// A STOP condition or repeated START condition has been received while still addressed as Slave
		// Repeated START enables the Master to switch between Slaves, Master Transmitter 
		// mode and Master Receiver mode without losing control over the bus.
		case (TW_SR_STOP):
			//Switched to the not addressed Slave mode; own SLA will be recognized; GCA will be recognized if TWGCE = “1”
			TWCR1 = (1 << TWEN1) | (1 << TWIE1) | (1 << TWINT1) | (1 << TWEA1);
			last_action = TWI_NO_ACTION;
			
			return TWI_RECEIVED_STOP;
		break;
		
		case (TW_SR_ARB_LOST_SLA_ACK):
		case (TW_SR_GCALL_ACK):
		case (TW_SR_ARB_LOST_GCALL_ACK):
		case (TW_SR_GCALL_DATA_ACK):
		case (TW_SR_GCALL_DATA_NACK):
		case (TW_ST_SLA_ACK):
		case (TW_BUS_ERROR):
	
		default:
			last_action = TWI_NO_ACTION;
			// debugging point to check status register
			TWCR1 = (1 << TWEN1) | (1 << TWIE1) | (1 << TWINT1) | (1 << TWEA1);
	}
}
*/


//
//1. The first step in a TWI transmission is to transmit a START condition. This is done by writing a
//specific value into TWCRn, instructing the TWI n hardware to transmit a START condition. Which
//value to write is described later on. However, it is important that the TWINT bit is set in the value
//written. Writing a one to TWINT clears the flag. The TWI n will not start any operation as long as
//the TWINT bit in TWCRn is set. Immediately after the application has cleared TWINT, the TWI n will
//initiate transmission of the START condition.

//2. When the START condition has been transmitted, the TWINT Flag in TWCRn is set, and TWSRn is
//updated with a status code indicating that the START condition has successfully been sent.

//3. The application software should now examine the value of TWSRn, to make sure that the START
//condition was successfully transmitted. If TWSRn indicates otherwise, the application software
//might take some special action, like calling an error routine. Assuming that the status code is as
//expected, the application must load SLA+W into TWDR. Remember that TWDRn is used both for
//address and data. After TWDRn has been loaded with the desired SLA+W, a specific value must
//be written to TWCRn, instructing the TWI n hardware to transmit the SLA+W present in TWDRn.
//Which value to write is described later on. However, it is important that the TWINT bit is set in the
//value written. Writing a one to TWINT clears the flag. The TWI will not start any operation as long
//as the TWINT bit in TWCRn is set. Immediately after the application has cleared TWINT, the TWI
//will initiate transmission of the address packet.

//4. When the address packet has been transmitted, the TWINT Flag in TWCRn is set, and TWSRn is
//updated with a status code indicating that the address packet has successfully been sent. The
//status code will also reflect whether a Slave acknowledged the packet or not.

//5. The application software should now examine the value of TWSRn, to make sure that the address
//packet was successfully transmitted, and that the value of the ACK bit was as expected. If TWSRn
//indicates otherwise, the application software might take some special action, like calling an error
//routine. Assuming that the status code is as expected, the application must load a data packet into
//TWDRn. Subsequently, a specific value must be written to TWCRn, instructing the TWI n hardware
//to transmit the data packet present in TWDRn. Which value to write is described later on. However,
//it is important that the TWINT bit is set in the value written. Writing a one to TWINT clears the flag.
//The TWI n will not start any operation as long as the TWINT bit in TWCRn is set. Immediately after
//the application has cleared TWINT, the TWI will initiate transmission of the data packet.

//6. When the data packet has been transmitted, the TWINT Flag in TWCRn is set, and TWSRn is
//updated with a status code indicating that the data packet has successfully been sent. The status
//code will also reflect whether a Slave acknowledged the packet or not.

//7. The application software should now examine the value of TWSRn, to make sure that the data
//packet was successfully transmitted, and that the value of the ACK bit was as expected. If TWSR
//indicates otherwise, the application software might take some special action, like calling an error
//routine. Assuming that the status code is as expected, the application must write a specific value to
//TWCRn, instructing the TWI n hardware to transmit a STOP condition. Which value to write is
//described later on. However, it is important that the TWINT bit is set in the value written. Writing a
//one to TWINT clears the flag. The TWI n will not start any operation as long as the TWINT bit in
//TWCRn is set. Immediately after the application has cleared TWINT, the TWI will initiate
//transmission of the STOP condition. Note that TWINT is not set after a STOP condition has been
//sent.
