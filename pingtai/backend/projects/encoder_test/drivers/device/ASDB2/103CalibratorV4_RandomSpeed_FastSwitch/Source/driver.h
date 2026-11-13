#ifndef DRIVER_H
#define DRIVER_H
#include "gd32f10x.h"
#include "def.h"

#define BUFFER_LENGTH (20)

typedef enum{
	DriverOn,
	DriverOff,
	DriverFindingZ
} DriverState;
typedef enum{
	DriverSpeedMode,
	DriverPositionMode
} DriverMode;
typedef enum{
	DriverCW,
	DriverCCW
} DriverRotation;

extern uint32_t currentPosition;


uint8_t instructionDisableEEPROM(void);
uint8_t instructionSwitchServo(DriverState state);
uint8_t instructionModeSelect(DriverMode mode);
uint8_t instructionSelectSpeed(uint8_t reg);
uint8_t instructionSetDirection(DriverRotation dir);
uint8_t instructionClearAlarm(void);
uint8_t instructionSetSpeedRegister(uint8_t reg, uint32_t speed);
uint8_t instructionSetSpeed(float speed);
uint8_t instructionSetABPluseNum(uint32_t pluseNum);
uint8_t instructionSelectPluseSource(void);
uint8_t instructionSetGearRatio(uint32_t molecule, uint32_t denominator);
void instructionMoveAngle(float angle);

uint8_t startMotor(void);
uint8_t stopMotor(void);
uint8_t reverseMotor(void);

uint8_t initDriver(uint32_t encoderTimer, uint32_t pluseTimer, uint32_t usart, IOPin driver485Control, IOPin driverLED, IOPin directionControl);


unsigned int CRC_Check(unsigned char *CRC_buf,unsigned char BuffLen);
uint8_t readRegister(uint16_t address, uint8_t registerNum, uint32_t timeout);
uint8_t writeSingleRegister(uint16_t address, uint16_t data, uint32_t timeout);
uint8_t writeSingleRegister32bit(uint16_t address, uint32_t data, uint32_t timeout);
uint8_t writeMultiRegister(uint16_t address, uint8_t registerNum, uint8_t * data, uint8_t dataByteNum, uint32_t timeout);

void updateDriverPosition(void);

#endif
