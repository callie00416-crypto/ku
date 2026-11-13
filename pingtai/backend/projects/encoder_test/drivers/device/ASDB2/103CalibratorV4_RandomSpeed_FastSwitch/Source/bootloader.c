#include "bootloader.h"
#include "tools.h"
#include "cdc_acm_core.h"

static uint32_t bootloaderUSART;
static uint32_t bootloaderUSARTReceiveDMA;
static uint32_t bootloaderUSARTReceiveDMAChannel;
static uint32_t bootloaderTimeoutCheckTimer;

static IOPin BootloaderLED;
static uint8_t * DMABuffer;
static uint16_t DMABufferLength;

static uint16_t lastCNT;
static uint16_t receiveSuccessLength;
static uint32_t receiveTimeout;


void initBootloader(uint32_t usart, uint32_t usartReceiveDMA, uint32_t usartReceiveDMAChannel, uint32_t timeoutCheckTimer, IOPin BootloaderLED_, uint8_t * buffer, uint16_t bufferLength){
	bootloaderUSART = usart;
	bootloaderUSARTReceiveDMA = usartReceiveDMA;
	bootloaderUSARTReceiveDMAChannel = usartReceiveDMAChannel;
	bootloaderTimeoutCheckTimer = timeoutCheckTimer;
	
	BootloaderLED = BootloaderLED_;
	
	DMABuffer = buffer;
	DMABufferLength = bufferLength;
	
	setDMALength(usartReceiveDMA, usartReceiveDMAChannel, bufferLength);
	usart_enable(usart);
}

void bootloaderReceiveCommand(){
	cdc_acm_data_receive(&usb_device_dev);
	if(usbReceivedLength){
		cdc_acm_data_send(&usb_device_dev, usbReceivedLength);
		usbReceivedLength = 0;
	}
}


void setDMAReceivedLengthTimtout(uint16_t length, uint32_t timeout){
	SysTickTimeoutInit(timeout);
	
	lastCNT = DMABufferLength;
	receiveSuccessLength = DMABufferLength - length;
	receiveTimeout = timeout;
}

int8_t checkDMAReceivedLengthTimeout(){
	uint8_t isTimeout = 0;
	uint16_t cnt = DMA_CHCNT(bootloaderUSARTReceiveDMA, bootloaderUSARTReceiveDMAChannel);
	if(cnt == lastCNT){
		if(!SysTickTimeoutCheck()){
			//isTimeout
			isTimeout = 1;
			return 1;
		}
	}else{
		if(cnt <= receiveSuccessLength){
			//Data all received
			return -1;
		}else{
			lastCNT = cnt;
			SysTickTimeoutInit(receiveTimeout);
		}
	}
	
	//No timeout, Still counting time
	return 0;
}


uint8_t checkBootloaderDMAReceiveTimeout(){
	while(1){
		int8_t isTimeout = checkDMAReceivedLengthTimeout();
		if(isTimeout == 1){
			//Timeout happend
			return 1;
		}else if(isTimeout == -1){
			//Timeout not happend, data All receive
			return 0;
		}
	}
}

void runCommand(uint8_t command){
	switch(command){
		case 0x00:
			//Get
			//HAL_UART_Transmit(currentUART, USBRxBuffer, DataLen, 1);
			//usartTransmit(bootloaderUSART, );
			setDMAReceivedLengthTimtout(100, 2e3);
			break;
	}
}
