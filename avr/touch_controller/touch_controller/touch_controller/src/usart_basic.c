/**
 * \file
 *
 * \brief USART basic driver.
 *
 *
 * Copyright (C) 2016 Atmel Corporation. All rights reserved.
 *
 * \asf_license_start
 *
 * \page License
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 * 3. The name of Atmel may not be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * 4. This software may only be redistributed and used in connection with an
 *    Atmel microcontroller product.
 *
 * THIS SOFTWARE IS PROVIDED BY ATMEL "AS IS" AND ANY EXPRESS OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT ARE
 * EXPRESSLY AND SPECIFICALLY DISCLAIMED. IN NO EVENT SHALL ATMEL BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 * ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 *
 * \asf_license_stop
 *
 *
 */
#include <compiler.h>
#include <clock_config.h>
#include <usart_basic.h>
#include <atomic.h>

int8_t USART_init()
{

	// Module is in UART mode

	/* Enable USART1 */
	PRR0 &= ~(1 << PRUSART1);

#define BAUD 38400

#include <utils/setbaud.h>

	UBRR1H = UBRRH_VALUE;
	UBRR1L = UBRRL_VALUE;

	UCSR1A = USE_2X << U2X1 /*  */
	         | 0 << MPCM1;  /* Multi-processor Communication Mode: disabled */

	UCSR1B = 0 << RXCIE1    /* RX Complete Interrupt Enable: disabled */
	         | 0 << TXCIE1  /* TX Complete Interrupt Enable: disabled */
	         | 0 << UDRIE1  /* USART Data Register Empty Interupt Enable: disabled */
	         | 0 << RXEN1   /* Receiver Enable: disabled */
	         | 1 << TXEN1   /* Transmitter Enable: enabled */
	         | 0 << UCSZ12; /*  */

	// UCSR1C = (0 << UMSEL11) | (0 << UMSEL10) /*  */
	//		 | (0 << UPM11) | (0 << UPM10) /* Disabled */
	//		 | 0 << USBS1 /* USART Stop Bit Select: disabled */
	//		 | (1 << UCSZ11) | (1 << UCSZ10); /* 8-bit */

	// UCSR1D = 0 << RXSIE /* USART RX Start Interrupt Enable: disabled */
	//		 | 0 << SFDE; /* Start Frame Detection Enable: disabled */

	return 0;
}

void USART_enable()
{
	UCSR1B |= ((1 << TXEN1) | (1 << RXEN1));
}

void USART_enable_rx()
{
	UCSR1B |= (1 << RXEN1);
}

void USART_enable_tx()
{
	UCSR1B |= (1 << TXEN1);
}

void USART_disable()
{
	UCSR1B &= ~((1 << TXEN1) | (1 << RXEN1));
}

uint8_t USART_get_data()
{
	return UDR1;
}

bool USART_is_tx_ready()
{
	return (UCSR1A & (1 << UDRE1));
}

bool USART_is_rx_ready()
{
	return (UCSR1A & (1 << RXC1));
}

bool USART_is_tx_busy()
{
	return (!(UCSR1A & (1 << TXC1)));
}

uint8_t USART_read()
{
	while (!(UCSR1A & (1 << RXC1)))
		;
	return UDR1;
}

void USART_write(const uint8_t data)
{
	while (!(UCSR1A & (1 << UDRE1)))
		;
	UDR1 = data;
}
