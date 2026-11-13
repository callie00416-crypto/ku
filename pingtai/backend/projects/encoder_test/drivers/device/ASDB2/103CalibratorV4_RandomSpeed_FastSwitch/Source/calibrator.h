#ifndef CALIBRATOR_H
#define CALIBRATOR_H

#include "gd32f10x.h"
#include "def.h"

typedef __PACKED_STRUCT {
	uint8_t index;
	uint16_t multi;
	uint16_t angle;
	uint32_t opticalPosition;

	uint16_t lastBatPolyfitIndex;
	uint16_t polyfitIndex;
	uint16_t batMulti;
	uint16_t enterBatMulti;
//	uint8_t plusTimes;
//	uint8_t minusTimes;
	uint16_t exitAngle;
	uint16_t enterAngle;
	uint16_t extraMulti;

	// uint16_t batteryEnterAngle;
	// uint16_t batteryExitAngle;
	// int16_t batteryEnterMulti;
	// int16_t batteryExitMulti;
	uint8_t batteryEnterCodeIndex;
	uint8_t batteryExitCodeIndex;
	uint8_t batteryMulti;
	uint8_t batteryProcess;
	uint8_t end1;
	uint8_t end2;
	uint8_t end3;
} SixHallDataPackage;



void initCalibrator(uint32_t usart, uint32_t usartReceiveDMA, uint32_t usartReceiveDMAChannel, uint32_t delayCheckTimer, IOPin bootloaderLED, IOPin SWDLED, void (** bootloaderHandler)(uint8_t * buffer));
void calibratorTransmit(uint8_t * buffer);
void checkCalibratorDMAReceiveTimeout(void);
void transmitIfExists();

#endif
