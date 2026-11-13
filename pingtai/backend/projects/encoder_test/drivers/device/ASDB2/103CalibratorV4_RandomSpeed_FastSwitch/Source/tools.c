#include "tools.h"
#include "gd32f10x_gpio.h"
#include "gd32f10x_usart.h"

void delayUS(uint32_t time){
	time *= SystemCoreClock / 4e6 ;
	while(time--);
}

void set485Transmit(uint32_t port, uint32_t pin){
	gpio_bit_set(port, pin);
}

void set485Receive(uint32_t port, uint32_t pin){
	gpio_bit_reset(port, pin);
}


void setDMALength(uint32_t dma, uint32_t dmaChannel, uint16_t length){
	dma_channel_disable(dma, dmaChannel);
	dma_flag_clear(dma, dmaChannel, DMA_FLAG_G);
	dma_transfer_number_config(dma, dmaChannel, length);
	dma_channel_enable(dma, dmaChannel);
}

//int8_t checkDMAReceiveTimeout(uint32_t dma, uint32_t dmaChannel, uint32_t delayTimer, uint8_t totalLength, uint8_t receiveSuccessLength, uint16_t timeoutMs, void (*timeoutHandler)(void)){
//	static uint16_t lastDMACounterValue;
//	
//	uint8_t clearTimer = 0;
//	uint8_t isReceived = 1;
//	uint16_t cnt = DMA_CHCNT(dma, dmaChannel);
//	
//	if(cnt == totalLength){
//		//Ready to read
//		//clear timer
//		clearTimer = 1;
//	}else{
//		if(cnt <= receiveSuccessLength){
//			isReceived = 1;
//		}else{
//			if(cnt == lastDMACounterValue){
//				//Check whether is timeout
//				if(timeoutHandler && TIMER_CNT(delayTimer) > timeoutMs){
//					(*timeoutHandler)();
//				}
//			}else{
//				//clear timer
//				clearTimer = 1;
//			}
//		}
//	}
//	
//	if(isReceived){
//		return 1;
//	}else if(clearTimer){
//		TIMER_CNT(delayTimer) = 0;
//		lastDMACounterValue = cnt;
//		
//		return 0;
//	}else{
//		
//	}
//}


//Timeout unit is us
void SysTickTimeoutInit(uint32_t timeoutUS){
	//Systick clocksource is set to HCKL / 8
	SysTick->CTRL = 0;
	SysTick->LOAD = (SystemCoreClock >> 3) / 1e6 * timeoutUS;
	SysTick->VAL = 0;
	SysTick->CTRL |= SysTick_CTRL_ENABLE_Msk;
}

//Return 1 if is timeout
uint32_t SysTickTimeoutCheck(){
	return SysTick->CTRL & SysTick_CTRL_COUNTFLAG_Msk;
}

void SysTickTimeoutDeinit(){
	SysTick->CTRL = 0;
}

uint8_t usartCheckTimeout(uint32_t usart, usart_flag_enum flag, uint32_t timeout){
	uint8_t isTimeout = 1;
	SysTickTimeoutInit(timeout);
	
	while(!SysTickTimeoutCheck()){
		if(usart_flag_get(usart, flag)){
			isTimeout = 0;
			usart_flag_clear(usart, flag);
			break;
		}
	}
	
	SysTickTimeoutDeinit();
	
	return isTimeout;
}

uint8_t usartTransmit(uint32_t usart, uint8_t * buffer, uint8_t length, uint32_t timeout){
	usart_flag_clear(usart, USART_FLAG_TC);
	while(length){
		usart_data_transmit(usart, *buffer++);
		if(usartCheckTimeout(usart, USART_FLAG_TC, timeout)){
			break;
		}
		length--;
	}
	
	if(length == 0){
		return 1;
	}else{
		return 0;
	}
}

uint8_t usartReceive(uint32_t usart, uint8_t * buffer, uint8_t length, uint32_t timeout){
	usart_flag_clear(usart, USART_FLAG_RBNE);
	while(length){
		if(usartCheckTimeout(usart, USART_FLAG_RBNE, timeout)){
			break;
		}else{
			*buffer++ = usart_data_receive(usart);
			length--;
		}
	}
	
	if(length == 0){
		return 1;
	}else{
		return 0;
	}
}
