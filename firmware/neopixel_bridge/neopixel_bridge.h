#ifndef NEOPIXEL_BRIDGE_H
#define NEOPIXEL_BRIDGE_H

// LED rings are controlled via this pin
#define CONTROL_PIN     6

// Total number of leds in the chain
#define LED_COUNT   60

#define SOP_MARKER      0xfd

// Whenever the protocol changes, this should be increased
#define PROTOCOL_VERSION    4

enum proto_commands {
    CMD_GET_MAX_LEDS,
    CMD_SET_NUM_LEDS,
    CMD_SET_LED,
    CMD_SET_LEDS,
    CMD_GET_PROTOCOL_VERSION,
    CMD_GET_LED,
    CMD_GET_LEDS,
    CMD_ROTATE_LEDS,
    CMD_ROTATE_LEDS_WITH_DELAY,
    CMD_INVALID = 0x7f,
};

#define RESPONSE_COMMAND_FLAG   ( 0x80 )
#define RESPONSE_COMMAND(x)     ( x | RESPONSE_COMMAND_FLAG )

#define LEN_CMD_SET_NUM_LEDS            1  // num leds
#define LEN_CMD_SET_LED                 4  // index, r, g, b
#define LEN_CMD_GET_LED                 1  // index
#define LEN_CMD_GET_LEDS                2  // index, number of leds
#define LEN_CMD_ROTATE_LEDS             1  // rotation count
#define LEN_CMD_ROTATE_LEDS_WITH_DELAY  2  // rotation count, delay ms.

enum proto_status {
    STATUS_OK,
    ERR_FAILED_TO_READ_HEADER,
    ERR_PACKET_TOO_LONG,
    ERR_PACKET_TOO_SHORT,
    ERR_FAILED_TO_READ_PACKET,
    ERR_WRONG_PACKET_SIZE,
    ERR_UNKNOWN_COMMAND,
    ERR_INDEX_TOO_LARGE,
};

#define MAX_DATA_SIZE   200

#endif  // NEOPIXEL_BRIDGE_H
