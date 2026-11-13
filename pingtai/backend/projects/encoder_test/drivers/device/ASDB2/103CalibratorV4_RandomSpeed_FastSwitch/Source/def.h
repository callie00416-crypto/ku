#ifndef DEF_H
#define DEF_H

typedef struct{
	uint32_t port;
	uint32_t pin;
} IOPin;

typedef struct{
	uint8_t CalibratorInitiating;
	uint8_t CalibratorConnecting;
	uint8_t CalibratorCalibrating;
	uint8_t CalibratorBootloading;
} CalibratorState;

#endif
