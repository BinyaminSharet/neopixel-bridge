#ifndef NEOPIXEL_BRIDGE_H
#define NEOPIXEL_BRIDGE_H

// LED rings are controlled via this pin
#define CONTROL_PIN		6

// Total number of leds in the chain
#define LED_COUNT		16


#define SOP_MARKER 		0xfd

enum proto_commands {
	CMD_GET_MAX_LEDS,
	CMD_SET_NUM_LEDS,
	CMD_SET_PATTERN,
	CMD_SET_LED,

	CMD_INVALID,
};

#define RESPONSE_CODE_FLAG	( 0x80 )
#define RESPONSE_CODE(x) 	( x | RESPONSE_CODE_FLAG )

#define LEN_CMD_SET_NUM_LEDS	1  // num leds
#define LEN_CMD_SET_LED			4  // index, r, g, b

enum proto_status {
	STATUS_OK,
	ERR_FAILED_TO_READ_HEADER,
	ERR_PACKET_TOO_LONG,
	ERR_FAILED_TO_READ_PACKET,
	ERR_WRONG_PACKET_SIZE,
	ERR_UNKNOWN_COMMAND,
};

#define MAX_DATA_SIZE	10

#endif  // NEOPIXEL_BRIDGE_H