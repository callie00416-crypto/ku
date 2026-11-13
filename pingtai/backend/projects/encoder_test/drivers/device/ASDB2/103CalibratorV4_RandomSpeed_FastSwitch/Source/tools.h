#ifndef TOOLS_H
#define TOOLS_H
#include "gd32f10x.h"
extern uint32_t SystemCoreClock;

void delayUS(uint32_t time);

uint8_t usartTransmit(uint32_t usart, uint8_t * buffer, uint8_t length, uint32_t timeout);
uint8_t usartReceive(uint32_t usart, uint8_t * buffer, uint8_t length, uint32_t timeout);
void set485Transmit(uint32_t port, uint32_t pin);
void set485Receive(uint32_t port, uint32_t pin);

void setDMALength(uint32_t dma, uint32_t dmaChannel, uint16_t length);
void checkDMAReceiveTimeout(uint32_t dma, uint32_t dmaChannel, uint32_t delayTimer, uint8_t totalLength, uint8_t receiveSuccessLength, uint16_t timeoutMs, void (*timeoutHandler)(void));

void SysTickTimeoutInit(uint32_t timeout);
uint32_t SysTickTimeoutCheck(void);
void SysTickTimeoutDeinit(void);

#endif
