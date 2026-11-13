#ifndef BOOTLOADER_H
#define BOOTLOADER_H

#include "gd32f10x.h"
#include "def.h"

void initBootloader(uint32_t usart, uint32_t usartReceiveDMA, uint32_t usartReceiveDMAChannel, uint32_t timeoutCheckTimer, IOPin BootloaderLED_, uint8_t * buffer, uint16_t bufferLength);

uint8_t checkBootloaderDMAReceiveTimeout();
void bootloaderReceiveCommand();

#endif
