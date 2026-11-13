#ifndef MAIN_H
#define MAIN_H
#include "gd32f10x.h"                   // Device header
#include "def.h"

void initClock(void);
void initNVIC(void);
void initUSB(IOPin);
void initGPIO(IOPin *, IOPin *, IOPin *, IOPin *, IOPin *, IOPin *, IOPin *);
void initDMA(void);
void initTimer(void);
void initUSART(void);
void initEXIT(void);

#define BOOTLOADER_SWD_DMA_MAX_LENGTH (300)

extern uint8_t BootloaderSWDUSARTDMABuffer[BOOTLOADER_SWD_DMA_MAX_LENGTH];

#endif
