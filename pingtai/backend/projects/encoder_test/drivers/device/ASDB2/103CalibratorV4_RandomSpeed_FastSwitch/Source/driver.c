#include "driver.h"
#include "tools.h"
#include "gd32f10x_gpio.h"              // GigaDevice::Device:GD32F10x_StdPeripherals:GPIO
#include "gd32f10x_usart.h"             // GigaDevice::Device:GD32F10x_StdPeripherals:USART

#define DELAY_US (1e4)
#define TIMEOUT_US (10000)
#define SPEED_REGISTER (3)
#define MOTOR_ONE_TURNSTEPS (160000UL)

#define CALIBRATION_SPEED_RPM (10.f)
#define CALIBRATION_DIRECTION DriverCW //DriverCCW-��ʱ�룬DriverCW-˳ʱ��

static uint8_t transmitBuffer[BUFFER_LENGTH];
static uint8_t receiveBuffer[BUFFER_LENGTH];
static uint16_t receivedUint16[BUFFER_LENGTH];

static uint32_t driverUSART;
static uint32_t driverEncoderTimer;
static uint32_t driverPluseTimer;

static IOPin driver485Control;
static IOPin driverLED;
static IOPin driverDirControl;

static DriverState currentState = DriverOff;
static DriverMode currentMode = DriverSpeedMode;
static DriverRotation currentDirection = DriverCW;

uint32_t currentPosition;
int16_t currentPositionHighWord;

float currentSpeed = 0;

static inline void toggleDriverLed(){
	GPIO_OCTL(driverLED.port) ^= driverLED.pin;
}

/**
	* Not use EEPROM
	* P2-30 to 5
	*/
uint8_t instructionDisableEEPROM(){
	//Not use EEPROM
	delayUS(DELAY_US);
	if(!writeSingleRegister(0x023C, 5, TIMEOUT_US))  
		return 0;
	
	return 1;
}


/**
	* Servo on
	* DI1
	*/
uint8_t instructionSwitchServo(DriverState state){
	uint16_t status = state == DriverOn ? 0x0001 : 0x0101;
	
	delayUS(DELAY_US);
	if(!writeSingleRegister(0x0214, status, TIMEOUT_US))
		return 0;
	
	return 1;
}


/**
	* Mode selection
  * P2-16 DI7 0x18
	* 0 Speed mode
	* 1 Position mode
	*/
uint8_t instructionModeSelect(DriverMode mode){
	uint16_t registerValue = 0x0018;
	
	if(mode == DriverSpeedMode){
		registerValue |= 1 << 8;
	}
	
	delayUS(DELAY_US);
	if(!writeSingleRegister(0x0220, registerValue, TIMEOUT_US))
		return 0;
	
	if(mode == DriverSpeedMode){
		delayUS(DELAY_US);
		if(!instructionSelectSpeed(SPEED_REGISTER))
			return 0;
	}else{
		delayUS(DELAY_US);
		if(!instructionSelectPluseSource())
			return 0;
		
		delayUS(DELAY_US);
		if(!instructionSetGearRatio(1, 1))
			return 0;
	}
	
	
	currentMode = mode;
	return 1;
}

/**

*/
uint8_t instructionPID_KPP(uint16_t value){
	delayUS(DELAY_US);
	if(!writeSingleRegister(0x0200, value, TIMEOUT_US))
		return 0;
	
	return 1;
}


/**
	* P1-00
	* 
	*/
uint8_t instructionSelectPluseSource(){
	uint16_t registerValue = 0
		| 2 << 0		//Pluse format
		| 4 << 4		//Filter width
		| 0 << 8		//Logic level
		| 1 << 12		//High speed pluse input
		;
	
	delayUS(DELAY_US);
	if(!writeSingleRegister(0x0100, registerValue, TIMEOUT_US))
		return 0;
	
	return 1;
}



/**
	* Set direction
	* DI6
	* CMDINV
	*/
uint8_t instructionSetDirection(DriverRotation dir){
	if(currentMode == DriverSpeedMode){
		uint16_t CMDINV = dir == DriverCW ? 0x0006 : 0x0106;
		
		delayUS(DELAY_US);
		if(!writeSingleRegister(0x021E, CMDINV, TIMEOUT_US)) 
			return 0;
	}else{
		if(dir == DriverCW){
			gpio_bit_reset(driverDirControl.port, driverDirControl.pin);
		}else{
			gpio_bit_set(driverDirControl.port, driverDirControl.pin);
		}
	}
	
	currentDirection = dir;
	return 1;
}


/**
	* Clear alarm
	*/
uint8_t instructionClearAlarm(){
	delayUS(DELAY_US);
	if(!writeSingleRegister(0x021C, 0x0102, TIMEOUT_US)) 
		return 0;
	
	return 1;
}

/**
	* reg must in [0,3]
	* DI3  DI4
	*	SPD1 SPD0
	*  0    0   	Analog input
	*  0    1			P1-09
	*  1    0     P1-10
	*  1    1     P1-11
	*/
uint8_t instructionSelectSpeed(uint8_t reg){
	uint16_t SPD0 = 0x0014;
	uint16_t SPD1 = 0x0015;
	
	if(reg > 3){
		return 0;
	}
	
	if(!(reg & 1)){
		SPD0 |= 1 << 8;
	}
	if(!(reg & 2)){
		SPD1 |= 1 << 8;
	}
	
	//SPD0, DI3
	delayUS(DELAY_US);
	if(!writeSingleRegister(0x0218, SPD0, TIMEOUT_US))
		return 0;
	
	//SPD1, DI4
	delayUS(DELAY_US);
	if(!writeSingleRegister(0x021A, SPD1, TIMEOUT_US))
		return 0;
	
	return 1;
}


/**
	* Set speed register
	*	SPD1 SPD0
	*  0    1			P1-09
	*  1    0     P1-10
	*  1    1     P1-11
	*/
uint8_t instructionSetSpeedRegister(uint8_t reg, uint32_t speed){
	uint16_t regAddress;
	switch(reg){
		case 1: regAddress = 0x0112; break;
		case 2: regAddress = 0x0114; break;
		case 3: regAddress = 0x0116; break;
		default: return 0;
	}
	
	delayUS(DELAY_US);
	if(!writeSingleRegister32bit(regAddress, speed, TIMEOUT_US))
		return 0;
	
	return 1;
}

/**
	* Select gear ratio molecule
	* Only one denominator(P1-45), and 4 molecule could be divided
	* but when GNUM0, GNUM1 is not set to DI pin, the molecule P1-44 will be selected
	*
	* Set gear ratio
	* 
	* K = molecule / denominator
	* if one turn needs 10000 pluses, after multi, one turn needs 10000*K pluses
	*/
uint8_t instructionSetGearRatio(uint32_t molecule, uint32_t denominator){
	//molecule
	delayUS(DELAY_US);
	if(!writeSingleRegister32bit(0x0158, molecule, TIMEOUT_US))
		return 0;
	
	//denominator
	delayUS(DELAY_US);
	if(!writeSingleRegister32bit(0x015A, denominator, TIMEOUT_US))
		return 0;
	
	return 1;
}

/**
	* Set speed, unit: rpm
	* ~Speed Mode
	* ~Position Mode
	*/
uint8_t instructionSetSpeed(float speed){
	if(currentMode == DriverSpeedMode){
		if(speed == 0){
			instructionSetSpeedRegister(SPEED_REGISTER, 0);
			delayUS(DELAY_US);
			instructionSwitchServo(DriverOff);
		}else{
			if(currentSpeed == 0){
				instructionSwitchServo(DriverOn);
				delayUS(DELAY_US);
			}
			instructionSetSpeedRegister(SPEED_REGISTER, speed * 10);
		}
	}else{		
		if(speed == 0){
			timer_disable(driverPluseTimer);
		}else{
			uint32_t period = SystemCoreClock / (speed * MOTOR_ONE_TURNSTEPS / 60) / 2;
			uint16_t prescaler = 0;
			uint32_t autoloadValue;
			
			do{
				prescaler++;
				autoloadValue = period / prescaler;
			}while(autoloadValue > (1UL << 16));
			
			
			timer_disable(driverPluseTimer);
			timer_prescaler_config(driverPluseTimer, prescaler - 1, TIMER_PSC_RELOAD_NOW);
			timer_counter_value_config(driverPluseTimer, 0);
			timer_autoreload_value_config(driverPluseTimer, autoloadValue - 1);
			timer_enable(driverPluseTimer);
		}
	}
	
	currentSpeed = speed;
	
	return 1;
}

void instructionMoveAngle(float angle){
	//pluse period
	uint32_t period = SystemCoreClock / (CALIBRATION_SPEED_RPM * MOTOR_ONE_TURNSTEPS / 60) / 2;
	uint16_t prescaler = 0;
	uint32_t autoloadValue;
	uint32_t pluseNum = angle * 2 / 360 * 160000UL;
	
	do{
		prescaler++;
		autoloadValue = period / prescaler;
	}while(autoloadValue > (1UL << 16));
	
	
	timer_disable(driverPluseTimer);
	timer_prescaler_config(driverPluseTimer, prescaler - 1, TIMER_PSC_RELOAD_NOW);
	timer_counter_value_config(driverPluseTimer, 0);
	timer_autoreload_value_config(driverPluseTimer, autoloadValue - 1);
	timer_enable(driverPluseTimer);
	
	TIMER_INTF(driverPluseTimer) = 0;
	while(pluseNum){
		if(TIMER_INTF(driverPluseTimer) & TIMER_INTF_UPIF){
			if(!--pluseNum){
				timer_disable(driverPluseTimer);
				break;
			}
		}
	}
}

/**
	*	P2-66 0x0284 16bit choose pluseNum multi 4 or not
	* P1-46 0x015C 32bit pluseNum, max 40000
	*/
uint8_t instructionSetABPluseNum(uint32_t pluseNum){
	if(pluseNum > 40000)
		return 0;
	
	if(!readRegister(0x0284, 1, TIMEOUT_US))
		return 0;
	uint16_t registerValue = receivedUint16[0];
	
	//set bit 15 to zero, set pluseNum to single num
	registerValue &= ~(1<<15);
	
	if(!writeSingleRegister(0x0284, registerValue, TIMEOUT_US))
		return 0;
	
	if(!writeSingleRegister32bit(0x015C, pluseNum, TIMEOUT_US))
		return 0;
	
	timer_enable(driverEncoderTimer);
	return 1;
}

uint8_t findZPhase(){
	currentState = DriverFindingZ;
	if(instructionSetSpeed(100)){
		//Find Z phase with 100rpm in 1s
		SysTickTimeoutInit(1000000);
		//Use Z phase external interrupt to set zero position
		exti_interrupt_enable(EXTI_10);
		//Disable encoder timer interrupt to avoid collision with Z phase interrupt
		timer_interrupt_disable(driverEncoderTimer, TIMER_INT_UP);
		
		while(!SysTickTimeoutCheck()){
			if(currentState != DriverFindingZ){
				break;
			}
		}
		
		SysTickTimeoutDeinit();
		
		
		timer_interrupt_enable(driverEncoderTimer, TIMER_INT_UP);
		if(currentState == DriverOn){
			return 1;
		}
	}
	
	return 0;
}

inline uint8_t startMotor(){
	return instructionSetSpeed(CALIBRATION_SPEED_RPM);
}

inline uint8_t stopMotor(){
	return instructionSetSpeed(0);
}

inline uint8_t reverseMotor(){
	return instructionSetDirection(currentDirection == DriverCCW ? DriverCW : DriverCCW);
}

/**
	* Control in P-S mixed mode, must set value to 6 in P1-01
	*/
uint8_t startDriver(){
	if( 1
		& instructionDisableEEPROM()
		& instructionSwitchServo(DriverOff)
		& instructionSetABPluseNum((4096) / 4)
	
		& instructionModeSelect(DriverSpeedMode)
//		& instructionModeSelect(DriverPositionMode)
		//& instructionPID_KPP(30)
	
		& instructionSetDirection(CALIBRATION_DIRECTION)
		& instructionSwitchServo(DriverOn)
	
		& findZPhase()
		& startMotor()
	)
		return 1;
	else
		return 0;
}

uint8_t connectDriver(uint8_t tryTimes){
	while(tryTimes){
		if(startDriver()){
			break;
		}
		tryTimes--;
	}
	
	return tryTimes;
}



uint8_t initDriver(uint32_t encoderTimer, uint32_t pluseTimer, uint32_t usart, IOPin driver485Control_, IOPin driverLED_, IOPin driverDirControl_){
	driverUSART = usart;
	driverEncoderTimer = encoderTimer;
	driverPluseTimer = pluseTimer;
	
	driver485Control = driver485Control_;
	driverLED = driverLED_;
	driverDirControl = driverDirControl_;
	
	return connectDriver(3);
}


unsigned int CRC_Check(unsigned char *CRC_buf,unsigned char BuffLen) {
	unsigned int CRC_ReturnValue = 0xFFFF;
	unsigned char i=0,j;
	while ( BuffLen -- ){
		CRC_ReturnValue ^= CRC_buf[i++];
		j = 8;
		do{
			if (CRC_ReturnValue & 0x01 ){
				CRC_ReturnValue = ( CRC_ReturnValue >> 1 ) ^ 0xA001;
			}else{
				CRC_ReturnValue = CRC_ReturnValue >> 1;
			}
			-- j;
		}while ( j ); 
	}
	
	return CRC_ReturnValue;
}

void formatResultToUint16(const uint8_t startIndex, const uint8_t uint16Length){
	uint8_t length = uint16Length;
	memset(receivedUint16, 0, length);
	while(length--){
		receivedUint16[length] = ((uint16_t)receiveBuffer[startIndex + length * 2] << 8) | (receiveBuffer[startIndex + 1 + length * 2]);
	}
}

//Each register is 16bit
uint8_t readRegister(uint16_t address, uint8_t registerNum, uint32_t timeout){
	static const uint8_t resultStartIndex = 3;

	uint8_t index = 0;
	set485Transmit(driver485Control.port, driver485Control.pin);
	delayUS(DELAY_US);

	//Device address
	transmitBuffer[index++] = 0x7F;
	//Read Function Code
	transmitBuffer[index++] = 0x03;
	
	//Register address
	transmitBuffer[index++] = (address & 0xFF00) >> 8;
	transmitBuffer[index++] = address & 0xFF;
	
	//Register num
	transmitBuffer[index++] = (registerNum & 0xFF00) >> 8;
	transmitBuffer[index++] = registerNum & 0xFF;
	
	uint16_t crc = CRC_Check((uint8_t *) transmitBuffer, index);
	transmitBuffer[index++] = crc & 0xFF;
	transmitBuffer[index++] = (crc & 0xFF00) >> 8;
	
	memset(receiveBuffer, 0, 5 + (registerNum << 1));
	if(usartTransmit(driverUSART,(uint8_t *) &transmitBuffer, index, timeout) == 0){
		return 0;
	}
	
	set485Receive(driver485Control.port, driver485Control.pin);
	if(usartReceive(driverUSART, (uint8_t *) &receiveBuffer, 5 + (registerNum << 1), timeout) == 0){
		return 0;
	}else{
		toggleDriverLed();
		formatResultToUint16(resultStartIndex, registerNum);
		
		return 5 + (registerNum << 1);
	}
}


uint8_t writeSingleRegister(uint16_t address, uint16_t data, uint32_t timeout){
	uint8_t index = 0;
	set485Transmit(driver485Control.port, driver485Control.pin);
	delayUS(DELAY_US);

	//Device address
	transmitBuffer[index++] = 0x7F;
	//Write Function Code
	transmitBuffer[index++] = 0x06;

	//Register address
	transmitBuffer[index++] = (address & 0xFF00) >> 8;
	transmitBuffer[index++] = address & 0xFF;

	//Data
	transmitBuffer[index++] = (data & 0xFF00) >> 8;
	transmitBuffer[index++] = data & 0xFF;

	uint16_t crc = CRC_Check((uint8_t *) transmitBuffer, index);
	transmitBuffer[index++] = crc & 0xFF;
	transmitBuffer[index++] = (crc & 0xFF00) >> 8;
	
	memset(receiveBuffer, 0, index);
	if(usartTransmit(driverUSART,(uint8_t *) &transmitBuffer, index, timeout) == 0){
		return 0;
	}
	
	set485Receive(driver485Control.port, driver485Control.pin);
	if(usartReceive(driverUSART, (uint8_t *) &receiveBuffer, index, timeout) == 0){
		return 0;
	}else{
		toggleDriverLed();
		return index;
	}
}


uint8_t writeSingleRegister32bit(uint16_t address, uint32_t data, uint32_t timeout){
	uint8_t dataByte[4] = {
		(data & 0x0000FF00) >> 8,
		(data & 0x000000FF) >> 0,
		(data & 0xFF000000) >> 24,
		(data & 0x00FF0000) >> 16,
	};
	
	return writeMultiRegister(address, 2, (uint8_t *) &dataByte, 4, timeout);
}


//Each register is 16bit
uint8_t writeMultiRegister(uint16_t address, uint8_t registerNum, uint8_t * data, uint8_t dataByteNum, uint32_t timeout){
	uint8_t index = 0;
	set485Transmit(driver485Control.port, driver485Control.pin);
	delayUS(DELAY_US);
	
	//Device address
	transmitBuffer[index++] = 0x7F;
	//Write Function Code
	transmitBuffer[index++] = 0x10;
	
	//Register address
	transmitBuffer[index++] = (address & 0xFF00) >> 8;
	transmitBuffer[index++] = address & 0xFF;
	
	//Register num
	transmitBuffer[index++] = (registerNum & 0xFF00) >> 8;
	transmitBuffer[index++] = registerNum & 0xFF;

	//Byte num
	transmitBuffer[index++] = dataByteNum;

	//Data byte num
	uint8_t tempIndex = 0;
	while(tempIndex < dataByteNum){
		transmitBuffer[index++] = data[tempIndex++];
	}
	
	uint16_t crc = CRC_Check((uint8_t *) transmitBuffer, index);
	transmitBuffer[index++] = crc & 0xFF;
	transmitBuffer[index++] = (crc & 0xFF00) >> 8;
	
	memset(receiveBuffer, 0, index);
	if(usartTransmit(driverUSART,(uint8_t *) &transmitBuffer, index, timeout) == 0){
		return 0;
	}
	
	set485Receive(driver485Control.port, driver485Control.pin);
	if(usartReceive(driverUSART, (uint8_t *) &receiveBuffer, 8, timeout) == 0){
		return 0;
	}else{
		toggleDriverLed();
		return 8;
	}
}

void updateDriverPosition(){
//	currentPosition &= ~0xFFFF;
//	currentPosition |= TIMER_CNT(driverEncoderTimer);
	
//	currentPosition = currentPositionHighWord << 16 | TIMER_CNT(driverEncoderTimer);
	currentPosition =  currentPositionHighWord << 16 | TIMER_CNT(driverEncoderTimer);
}

uint16_t irqtimes = 0;
/**
	* Increase higher word
	*/
void TIMER0_UP_IRQHandler(){
	TIMER_INTF(driverEncoderTimer) &= ~TIMER_FLAG_UP;
	if(TIMER_CTL0(driverEncoderTimer) & TIMER_CTL0_DIR){
		currentPositionHighWord--;
	}else{
		currentPositionHighWord++;
	}
//	if(TIMER_CNT(driverEncoderTimer) < 100){
//		currentPositionHighWord++;
//	}else{
//		currentPositionHighWord--;
//	}
	
	
//	if(currentPositionHighWord > 1){
//		currentPositionHighWord -= 2;
//	}else if(currentPositionHighWord < 0){
//		currentPositionHighWord += 2;
//	}
//	irqtimes++;
	
//	currentPosition ^= 1UL << 16;
//	updateDriverPosition();
}
/**
	* Detect Z phase, refer to findZPhase function
	* trigger one time after startDriver
	*/
void EXTI10_15_IRQHandler(){
	EXTI_PD = EXTI_10;
	
	//Set timer zero position
	TIMER_CNT(TIMER0) = 0;
	currentPosition = 0;
	
	//end findZPhase
	currentState = DriverOn;
	
	//disable interrupt
	exti_interrupt_disable(EXTI_10);
}
