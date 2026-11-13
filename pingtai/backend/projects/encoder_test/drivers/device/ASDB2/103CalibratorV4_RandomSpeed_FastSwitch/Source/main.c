#include "main.h"
#include "tools.h"
#include "cdc_acm_core.h"
#include "driver.h"
#include "calibrator.h"
#include "bootloader.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

static IOPin USBLed;
static IOPin BootloaderLED;
static IOPin SWDLED;
static IOPin DriverLED;
static IOPin Driver485Control;
static IOPin DriverDirectionControl;
static IOPin USBControl;

uint8_t BootloaderSWDUSARTDMABuffer[BOOTLOADER_SWD_DMA_MAX_LENGTH];
void (*BootloaderSWDUSARTDMAHandler)(uint8_t * buffer);

uint32_t timer3Counter = 0;
uint16_t lastAngle = 0;

volatile uint8_t usb_tx_enabled = 0;
typedef struct {
    uint8_t active;
    uint32_t startTick;
    uint32_t duration;
    float speed_rpm;
} MotorTimedTask;

MotorTimedTask timedTask = {0};

extern uint8_t usb_data_buffer[CDC_ACM_DATA_PACKET_SIZE];
extern uint8_t usb_tx_buffer[CDC_ACM_DATA_PACKET_SIZE];
extern uint8_t usbPackageReceive;
extern uint32_t usbReceivedLength;

static void updateMulti(void);
static void startTimedRotation(float speed_rpm, uint32_t duration_ms, DriverRotation dir);
static void processUSBCommand(void);

extern usbd_core_handle_struct usb_device_dev;
extern uint8_t usbPackageSent;

void initClock(void) {
    rcu_usb_clock_config(RCU_CKUSB_CKPLL_DIV2_5);
    rcu_periph_clock_enable(RCU_GPIOA);
    rcu_periph_clock_enable(RCU_GPIOB);
    rcu_periph_clock_enable(RCU_USART1);
    rcu_periph_clock_enable(RCU_USART0);
    rcu_periph_clock_enable(RCU_DMA0);
    rcu_periph_clock_enable(RCU_AF);
    rcu_periph_clock_enable(RCU_USBD);
    rcu_periph_clock_enable(RCU_TIMER0);
    rcu_periph_clock_enable(RCU_TIMER1);
    rcu_periph_clock_enable(RCU_TIMER2);
    rcu_periph_clock_enable(RCU_TIMER3);
}

void initNVIC(void) {
    nvic_priority_group_set(NVIC_PRIGROUP_PRE2_SUB2);
}

void initUSB(IOPin USBControl) {
    usbd_core_init(&usb_device_dev);
    nvic_irq_enable(USBD_LP_CAN0_RX0_IRQn, 2, 0);
    gpio_bit_reset(USBControl.port, USBControl.pin);
    delayUS(1000);
    gpio_bit_set(USBControl.port, USBControl.pin);
}

void initGPIO(IOPin * DriverLEDPtr, IOPin * SWDLEDPtr, IOPin * BootloaderLEDPtr,
              IOPin * USBLedPtr, IOPin * Driver485ControlPtr,
              IOPin * DriverDirControlPtr, IOPin * USBControlPtr) {
    /* Bootloader / SWD */
    gpio_init(GPIOA, GPIO_MODE_OUT_PP, GPIO_OSPEED_10MHZ, GPIO_PIN_0);
    gpio_init(GPIOA, GPIO_MODE_OUT_PP, GPIO_OSPEED_10MHZ, GPIO_PIN_1);
    gpio_init(GPIOA, GPIO_MODE_OUT_PP, GPIO_OSPEED_10MHZ, GPIO_PIN_2);
    gpio_init(GPIOA, GPIO_MODE_IN_FLOATING, GPIO_OSPEED_10MHZ, GPIO_PIN_3);
    gpio_init(GPIOB, GPIO_MODE_OUT_PP, GPIO_OSPEED_10MHZ, GPIO_PIN_9);

    /* LED */
    DriverLEDPtr->port = GPIOA;  DriverLEDPtr->pin = GPIO_PIN_4;
    gpio_init(DriverLEDPtr->port, GPIO_MODE_OUT_PP, GPIO_OSPEED_2MHZ, DriverLEDPtr->pin);
    SWDLEDPtr->port = GPIOA;     SWDLEDPtr->pin = GPIO_PIN_5;
    gpio_init(SWDLEDPtr->port, GPIO_MODE_OUT_PP, GPIO_OSPEED_2MHZ, SWDLEDPtr->pin);
    BootloaderLEDPtr->port = GPIOA; BootloaderLEDPtr->pin = GPIO_PIN_6;
    gpio_init(BootloaderLEDPtr->port, GPIO_MODE_OUT_PP, GPIO_OSPEED_2MHZ, BootloaderLEDPtr->pin);
    USBLedPtr->port = GPIOA;     USBLedPtr->pin = GPIO_PIN_7;
    gpio_init(USBLedPtr->port, GPIO_MODE_OUT_PP, GPIO_OSPEED_2MHZ, USBLedPtr->pin);

    /* Driver */
    gpio_init(GPIOA, GPIO_MODE_IN_FLOATING, GPIO_OSPEED_50MHZ, GPIO_PIN_8);
    gpio_init(GPIOA, GPIO_MODE_IN_FLOATING, GPIO_OSPEED_50MHZ, GPIO_PIN_9);
    gpio_init(GPIOA, GPIO_MODE_IN_FLOATING, GPIO_OSPEED_50MHZ, GPIO_PIN_10);
    gpio_init(GPIOB, GPIO_MODE_AF_PP, GPIO_OSPEED_10MHZ, GPIO_PIN_10);
    DriverDirControlPtr->port = GPIOB; DriverDirControlPtr->pin = GPIO_PIN_2;
    gpio_init(DriverDirControlPtr->port, GPIO_MODE_OUT_PP, GPIO_OSPEED_10MHZ, DriverDirControlPtr->pin);
    Driver485ControlPtr->port = GPIOB; Driver485ControlPtr->pin = GPIO_PIN_5;
    gpio_init(Driver485ControlPtr->port, GPIO_MODE_OUT_PP, GPIO_OSPEED_10MHZ, Driver485ControlPtr->pin);
    gpio_init(GPIOB, GPIO_MODE_AF_PP, GPIO_OSPEED_10MHZ, GPIO_PIN_6);
    gpio_init(GPIOB, GPIO_MODE_IN_FLOATING, GPIO_OSPEED_10MHZ, GPIO_PIN_7);
    gpio_pin_remap_config(GPIO_USART0_REMAP, ENABLE);
    gpio_pin_remap_config(GPIO_TIMER1_FULL_REMAP, ENABLE);

    /* USB */
    USBControlPtr->port = GPIOA; USBControlPtr->pin = GPIO_PIN_15;
    gpio_init(USBControlPtr->port, GPIO_MODE_OUT_PP, GPIO_OSPEED_2MHZ, USBControlPtr->pin);
    gpio_pin_remap_config(GPIO_SWJ_SWDPENABLE_REMAP, ENABLE);
}

void initDMA(void) {
    dma_circulation_enable(DMA0, DMA_CH5);
    dma_transfer_direction_config(DMA0, DMA_CH5, DMA_PERIPHERAL_TO_MEMORY);
    dma_periph_address_config(DMA0, DMA_CH5, (uint32_t) &USART_DATA(USART1));
    dma_memory_address_config(DMA0, DMA_CH5, (uint32_t) BootloaderSWDUSARTDMABuffer);
    dma_periph_width_config(DMA0, DMA_CH5, DMA_MEMORY_WIDTH_8BIT);
    dma_memory_width_config(DMA0, DMA_CH5, DMA_MEMORY_WIDTH_8BIT);
    dma_memory_increase_enable(DMA0, DMA_CH5);
    dma_priority_config(DMA0, DMA_CH5, DMA_PRIORITY_HIGH);
    dma_interrupt_enable(DMA0, DMA_CH5, DMA_INT_FTF | DMA_INT_ERR);
    nvic_irq_enable(DMA0_Channel5_IRQn, 0, 0);
}

void initUSART(void) {
    usart_baudrate_set(USART0, 115200);
    usart_parity_config(USART0, USART_PM_NONE);
    usart_word_length_set(USART0, USART_WL_8BIT);
    usart_stop_bit_set(USART0, USART_STB_2BIT);
    usart_enable(USART0);
    usart_receive_config(USART0, USART_RECEIVE_ENABLE);
    usart_transmit_config(USART0, USART_TRANSMIT_ENABLE);

    usart_baudrate_set(USART1, 2500000);
    usart_parity_config(USART1, USART_PM_NONE);
    usart_word_length_set(USART1, USART_WL_8BIT);
    usart_stop_bit_set(USART1, USART_STB_1BIT);
    usart_receive_config(USART1, USART_RECEIVE_ENABLE);
    usart_transmit_config(USART1, USART_TRANSMIT_ENABLE);
    usart_dma_receive_config(USART1, USART_DENR_ENABLE);
}

void initTimer(void) {
    timer_slave_mode_select(TIMER0, TIMER_ENCODER_MODE2);
    timer_autoreload_value_config(TIMER0, 4095);

    timer_autoreload_value_config(TIMER1, 0xFFF);
    timer_auto_reload_shadow_disable(TIMER1);
    timer_channel_output_mode_config(TIMER1, TIMER_CH_2, TIMER_OC_MODE_TOGGLE);
    timer_channel_output_state_config(TIMER1, TIMER_CH_2, TIMER_CCX_ENABLE);

    timer_prescaler_config(TIMER2, rcu_clock_freq_get(CK_APB1) / 10000, TIMER_PSC_RELOAD_NOW);
    timer_autoreload_value_config(TIMER2, 0xFFFF);
    timer_enable(TIMER2);

    timer_prescaler_config(TIMER3, rcu_clock_freq_get(CK_APB1) / 10000, TIMER_PSC_RELOAD_NOW);
    timer_autoreload_value_config(TIMER3, 1);
    timer_update_event_enable(TIMER3);
    timer_interrupt_enable(TIMER3, TIMER_INT_UP);
    timer_interrupt_flag_clear(TIMER3, TIMER_INT_FLAG_UP);
    nvic_irq_enable(TIMER3_IRQn, 0, 1);
    timer_enable(TIMER3);
}

void initEXIT(void) {
    gpio_exti_source_select(GPIO_PORT_SOURCE_GPIOA, GPIO_PIN_SOURCE_10);
    EXTI_RTEN |= EXTI_10;
    EXTI_FTEN &= ~EXTI_10;
    nvic_irq_enable(EXTI10_15_IRQn, 0, 0);
}

void DMA0_Channel5_IRQHandler(void) {
    uint32_t flags = DMA_INTF(DMA0);
    DMA_INTC(DMA0) |= DMA_INTC_GIFC << (5 * 4);
    if (!(flags & DMA_FLAG_ERR)) {
        (*BootloaderSWDUSARTDMAHandler)(BootloaderSWDUSARTDMABuffer);
    }
}

void TIMER3_IRQHandler(void) {
    TIMER_INTF(TIMER3) &= ~TIMER_FLAG_UP;
    timer3Counter++;
    updateMulti();

    if (timedTask.active) {
        if ((timer3Counter - timedTask.startTick) >= timedTask.duration) {
            instructionSetSpeed(0.0f);
            timedTask.active = 0;
        }
    }

//    if ((timer3Counter % 100) == 0) {
//        transmitIfExists();
//    }
}

static void updateMulti(void) {
    static int16_t multi = 0;
    uint16_t angle = TIMER_CNT(TIMER0);

    if (lastAngle > (uint16_t)((1<<12) * 0.8) && angle < (uint16_t)((1<<12) * 0.2)) {
        multi++;
    } else if (lastAngle < (uint16_t)((1<<12) * 0.2) && angle > (uint16_t)((1<<12) * 0.8)) {
        multi--;
    }

    currentPosition = multi << 16 | angle;
    lastAngle = angle;
}

static void startTimedRotation(float speed_rpm, uint32_t duration_ms, DriverRotation dir) {
    #define TICK_PER_MS 5   
    timedTask.active = 1;
    timedTask.startTick = timer3Counter;
    timedTask.duration = duration_ms * TICK_PER_MS;
    timedTask.speed_rpm = speed_rpm;

    instructionSetDirection(dir);
    instructionSetSpeed(speed_rpm);
}

static void processUSBCommand(void) {
    char *cmd = (char *)usb_data_buffer;
    usb_data_buffer[CDC_ACM_DATA_PACKET_SIZE - 1] = '\0';

    if (strncmp(cmd, "PING", 4) == 0) {
        usb_tx_enabled = 1; 
        strcpy((char *)usb_tx_buffer, "PONG\n");
        cdc_acm_data_send(&usb_device_dev, 5);
        return;
    }

    if (strncmp(cmd, "RUN", 3) == 0) {
        float speed;
        uint32_t time_ms;
        char dir_str[4] = {0};
        if (sscanf(cmd, "RUN %f %u %3s", &speed, &time_ms, dir_str) == 3) {
            DriverRotation dir = (strncmp(dir_str, "CCW", 3) == 0) ? DriverCCW : DriverCW;
            
            if (timedTask.active) {
                instructionSetSpeed(0.0f);
                timedTask.active = 0;
            }
            startTimedRotation(speed, time_ms, dir);

            usb_tx_enabled = 1;
            strcpy((char *)usb_tx_buffer, "OK\n");
            cdc_acm_data_send(&usb_device_dev, 3);
        }
        return;
    }

    if (strncmp(cmd, "STOP", 4) == 0) {
        instructionSetSpeed(0.0f);
        timedTask.active = 0;

        usb_tx_enabled = 1;
        strcpy((char *)usb_tx_buffer, "OK\n");
        cdc_acm_data_send(&usb_device_dev, 3);
        return;
    }
}

int main(void) {
    initClock();
    initNVIC();
    initGPIO(&DriverLED, &SWDLED, &BootloaderLED, &USBLed,
             &Driver485Control, &DriverDirectionControl, &USBControl);
    initUSB(USBControl);
    initTimer();
    initDMA();
    initUSART();
    initEXIT();

    initDriver(TIMER0, TIMER1, USART0, Driver485Control, DriverLED, DriverDirectionControl);
    initCalibrator(USART1, DMA0, DMA_CH5, TIMER2, BootloaderLED, SWDLED,
                   &BootloaderSWDUSARTDMAHandler);

    lastAngle = TIMER_CNT(TIMER0);

    while (1) {
        checkCalibratorDMAReceiveTimeout();
        if (usbPackageReceive) {
            processUSBCommand();
            usbPackageReceive = 0;
            usbReceivedLength = 0;
        }
    }
}