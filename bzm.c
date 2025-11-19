#include <stdint.h>
#include <stdbool.h>
#include "main.h"
#include "bzm.h"
#include "display.h"

/* Buffer used for reception */
uint16_t rxbuf[RXBUFFERSIZE];

UART_HandleTypeDef huart6;
DMA_HandleTypeDef hdma_usart6_rx;

volatile uint8_t rxdone = 0;

void HAL_UARTEx_RxEventCallback(UART_HandleTypeDef *huart, uint16_t rx_len);
static uint16_t BZM_transfer(uint16_t * txbuf, uint16_t * response, uint8_t len);

//init UART
void BZM_UART_Init(void) {
    huart6.Instance = USART6;
    huart6.Init.BaudRate = 5000000;
    huart6.Init.WordLength = UART_WORDLENGTH_9B;
    huart6.Init.StopBits = UART_STOPBITS_1;
    huart6.Init.Parity = UART_PARITY_NONE;
    huart6.Init.Mode = UART_MODE_TX_RX;
    huart6.Init.HwFlowCtl = UART_HWCONTROL_NONE;
    huart6.Init.OverSampling = UART_OVERSAMPLING_16;

    if (HAL_UART_Init(&huart6) != HAL_OK) {
        Error_Handler();
    }

    HAL_UART_RegisterRxEventCallback(&huart6, HAL_UARTEx_RxEventCallback);
}

void BZM_initGPIO(void) {
    GPIO_InitTypeDef  GPIO_InitStruct;

    /* Configure PA07 IO in output push-pull mode to be chip reset ###*/  
    GPIO_InitStruct.Pin = BZM_RESET_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    GPIO_InitStruct.Speed = GPIO_SPEED_FAST;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    HAL_GPIO_WritePin(GPIOA, BZM_RESET_PIN, 0);

    //configure PA11 and PA12 to use alternate function 8 (USART6)
    GPIO_InitStruct.Pin = GPIO_PIN_11 | GPIO_PIN_12;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Alternate = GPIO_AF8_USART6;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

}

void BZM_ToggleGPIO(void) {
    HAL_GPIO_WritePin(GPIOA, BZM_RESET_PIN, 0);
    HAL_Delay(100);
    HAL_GPIO_WritePin(GPIOA, BZM_RESET_PIN, 1);
    HAL_Delay(100);
}


//function to reverse the order of bytes in a 16 bit integer
uint16_t bswap_16(uint16_t x) {
    return (x >> 8) | (x << 8);
}


uint16_t BZM_send_noop(uint8_t asic, uint16_t * response, bool debug) {
    uint16_t buf[2];

    buf[0] = 0x100 | asic; //address with 9th bit high
    buf[1] = 0x000 | BZ2_OP_NOOP; //data BZ2_OP_NOOP, 9th bit low, high nibble

    //debug buf bytes
    if (debug){
        printf("Send NOOP: ");
        print_hex_bytes(buf, 2);
    }

    uint16_t rx_size = BZM_transfer(buf, response, 2);
    if (rx_size == 0) {
        printf("BZM_transfer failed\n");
        return 0;
    } else {
        return rx_size;
    }
}

/// @brief BZM_readreg reads from a register on the BZM
/// @param asic ASIC address. 0xFA is the default
/// @param engine_id seems like 0xFFF is the default
/// @param offset this is the register address
/// @param count the number of bytes to read
/// @param response buffer for the response
/// @return the number of bytes read
uint16_t BZM_readreg(uint8_t asic, uint16_t engine_id, uint8_t offset, uint16_t count, uint16_t * response, bool debug) {
    uint16_t buf[8];

    //ASIC address first, with 9th bit high
    buf[0] = 0x0100 | asic; //address with 9th bit high

    //Data next, with 9th bit low
    buf[1] = 0x0000 | BZ2_OP_READREG | ((engine_id & 0x0F00) >> 8); //data BZ2_OP_READREG, and the high 4 bytes of engine_id
    buf[2] = 0x0000 | (engine_id & 0xFF); //engineID
    buf[3] = 0x0000 | offset; //offset (register address)
    buf[4] = count - 1; //byte count
    buf[5] = 0x0000; //TAR

    if (debug) {
        printf("Send readreg: ");
        print_hex_bytes(buf, 5);
    }

    uint16_t rx_size = BZM_transfer(buf, response, 5);
    if (rx_size == 0) {
        printf("BZM_transfer failed\n");
        return 0;
    } else {
        return rx_size;
    }
}

/// @brief BZM_writereg writes to a register on the BZM
/// @param asic ASIC address. 0xFA is the default
/// @param engine_id seems like 0xFFF is the default
/// @param offset this is the register address
/// @param write_data the data to write
/// @param count the number of bytes to write
/// @return true if the transmit was successful
bool BZM_writereg(uint8_t asic, uint16_t engine_id, uint8_t offset, uint8_t * write_data, uint16_t count, bool debug) {
    uint16_t buf[100];
    uint8_t idx = 0;

    //ASIC address first, with 9th bit high
    buf[0] = 0x0100 | asic; //address with 9th bit high

    //Data next, with 9th bit low
    buf[1] = 0x0000 | BZ2_OP_WRITEREG | ((engine_id & 0x0F00) >> 8); //data BZ2_OP_WRITEREG, and the high 4 bytes of engine_id
    buf[2] = 0x0000 | (engine_id & 0xFF); //engineID
    buf[3] = 0x0000 | offset; //offset (register address)
    buf[4] = count-1; //byte count
    idx = 5;

    //copy write_data to buf
    for (int i = 0; i < count; i++) {
        buf[i+idx] = 0x0000 | write_data[i];
    }

    idx += count;

    //set the term at the end
    buf[idx] = 0x0000;

    idx++;

    //debug buf bytes
    if (debug) {
        printf("Send writereg: ");
        print_hex_bytes(buf, idx);
    }

    //send the write data
    //send txbuf on UART6
    return (HAL_UART_Transmit(&huart6, (char *)buf, idx, 0xFFFF) == HAL_OK);
}

//this might only work in TDM mode?
uint16_t BZM_readVoltage(uint8_t asic, uint16_t * response) {
    uint16_t buf[8];

    //ASIC address first, with 9th bit high
    buf[0] = 0x0100 | asic; //address with 9th bit high

    //Data next, with 9th bit low
    buf[1] = 0x0000 | BZ2_OP_TSVSREAD;

    //debug buf bytes
    printf("Send readSensors: ");
    print_hex_bytes(buf, 2);

    uint16_t rx_size = BZM_transfer(buf, response, 2);
    if (rx_size == 0) {
        printf("BZM_transfer failed\n");
        return 0;
    } else {
        return rx_size;
    }
}


uint16_t BZM_loopback(uint8_t asic, uint8_t * data, uint8_t count, uint16_t * response) {
    uint16_t buf[50];

    buf[0] = 0x100 | asic; //address with 9th bit high
    buf[1] = 0x000 | BZ2_OP_LOOPBACK; //data BZ2_OP_LOOPBACK, 9th bit low, high nibble
    buf[2] = count-1; //byte count
    buf[3] = 0x0000; //TAR

    for (int i = 0; i < count; i++) {
        buf[i+4] = 0x0000 | data[i];
    }

    //debug buf bytes
    printf("Send Loopback: ");
    print_hex_bytes(buf, count+4);

    uint16_t rx_size = BZM_transfer(buf, response, count+4);
    if (rx_size == 0) {
        printf("BZM_transfer failed\n");
        return 0;
    } else {
        return rx_size;
    }
}

//transfer function transmits txbuf and receives a response into response
//returns the number of bytes received or 0 if failure
static uint16_t BZM_transfer(uint16_t * txbuf, uint16_t * response, uint8_t len) {
     //Put UART peripheral in reception process  
    rxdone = 0; //reset the flag
    if(HAL_UARTEx_ReceiveToIdle_DMA(&huart6, (uint8_t *)rxbuf, RXBUFFERSIZE) != HAL_OK) {
        Error_Handler();
        return false;
    }

    //send txbuf on UART6
    HAL_UART_Transmit(&huart6, (char *)txbuf, len, 0xFFFF);

    //wait for DMA RX to finish or 2 seconds, whichever comes first
    uint32_t startTick = HAL_GetTick();
    while (rxdone == 0) {
        if (HAL_GetTick() - startTick > 2000) {
            return false;
        }
    }

    //send terminating character
    HAL_UART_Transmit(&huart6, "\0", 1, 0xFFFF);

    //debug rxbuf
    // printf("rxbuf(%d): ", rxdone);
    // print_hex_bytes(rxbuf, rxdone);

    //copy rxbuf to response
    for (int i = 0; i < rxdone; i++) {
        response[i] = rxbuf[i];
    }

    return rxdone;
}

//UART RX Event Callback
void HAL_UARTEx_RxEventCallback(UART_HandleTypeDef *huart, uint16_t rx_len) {
    //check to see if the event is a DMA TransferComplete or IDLE
    if (HAL_UARTEx_GetRxEventType(huart) == HAL_UART_RXEVENT_TC || HAL_UARTEx_GetRxEventType(huart) == HAL_UART_RXEVENT_IDLE) {
        HAL_UART_DMAStop(huart);
        rxdone = rx_len;
    }
}


/**
  * @brief This function handles USART6 global interrupt.
  * very unclear why this is needed, but you definitely do
  */
void USART6_IRQHandler(void) {

    HAL_UART_IRQHandler(&huart6);

}