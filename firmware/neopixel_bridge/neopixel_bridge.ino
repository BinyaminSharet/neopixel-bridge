#include <FastLED.h>
#include "neopixel_bridge.h"

// When working with leds regardless of their ring
// fixup the index
#define FIXIDX(x)	( x )

CHSV hsvs[LED_COUNT] = {};
CRGB leds[LED_COUNT] = { 0 };
CRGB tmp_leds[LED_COUNT] = { 0 };

uint8_t user_num_leds = LED_COUNT;

void setup()
{
	Serial.begin(115200);
	FastLED.addLeds<NEOPIXEL, CONTROL_PIN>(leds, LED_COUNT);
	turn_off_leds(0, LED_COUNT);
	FastLED.show();
}


void set_led_rgb(uint8_t idx, uint8_t r, uint8_t g, uint8_t b) {
	leds[FIXIDX(idx)] = CRGB(r, g, b);
}

void get_led_rgb(uint8_t idx, uint8_t * p_rgb) {
	*p_rgb++ = leds[FIXIDX(idx)].red;
	*p_rgb++ = leds[FIXIDX(idx)].green;
	*p_rgb++ = leds[FIXIDX(idx)].blue;
}

// set the rgb color to a range of leds
// from - from led
// to - to led (exclusive)
void set_range_rgb(uint8_t from, uint8_t to, uint8_t r, uint8_t g, uint8_t b) {
	while (from < to) {
		set_led_rgb(from, r, g, b);
		++from;
	}
}

// turn off leds in a given range leds in a given range to 
// from - from led
// to - to led (exclusive)
void turn_off_leds(uint8_t from, uint8_t to) {
	set_range_rgb(from, to, 0, 0, 0);
}

void rotate_leds_single() {
  CRGB first = leds[FIXIDX(0)];
  for (int i = 0; i < user_num_leds - 1; ++i) {
    leds[FIXIDX(i)] = leds[FIXIDX(i + 1)];
  }
  leds[FIXIDX(user_num_leds - 1)] = first;
}

void rotate_leds(uint8_t count) {
  while(count--) {
    rotate_leds_single();
  }
}

// basic header of both command and response
// the len is the length of all data that appears after it
struct comm_header {
	uint8_t command;
	uint8_t len;
};

#define COMM_HEADER_SIZE	( 2 )

struct comm_response_header {
	struct comm_header header;
	uint8_t status;
};

#define COMM_RESP_HEADER_SIZE	( COMM_HEADER_SIZE + 1 )

#define FAIL(x) 	do { status = x; goto error_case; } while( 0 )
#define ASSERT(cond, x)		do { if (!(cond)) FAIL(x); } while( 0 )
#define ASSERT_LEN(header, len) do { ASSERT((header->len == len), ERR_WRONG_PACKET_SIZE); } while ( 0 )

uint8_t handle_command(struct comm_header * header, uint8_t * data, uint8_t * resp, uint8_t * resp_len)
{
	uint8_t status = STATUS_OK;
	*resp_len = 0;
	switch(header->command) {
		case CMD_GET_MAX_LEDS:
			*resp = LED_COUNT;
			*resp_len = 1;
			break;
		case CMD_SET_NUM_LEDS:
			ASSERT(header->len == LEN_CMD_SET_NUM_LEDS, ERR_WRONG_PACKET_SIZE);
			user_num_leds = data[0];
			break;
		case CMD_SET_LED:
			ASSERT(header->len == LEN_CMD_SET_LED, ERR_WRONG_PACKET_SIZE);
			set_led_rgb(data[0], data[1], data[2], data[3]);
			FastLED.show();
			break;
		case CMD_SET_LEDS:
		{
			uint8_t idx = data[0];
			uint8_t num_leds = (header->len - 1) / 3;
			uint8_t color_idx = 1;
			ASSERT(header->len > 1, ERR_PACKET_TOO_SHORT);
			ASSERT(idx < user_num_leds, ERR_INDEX_TOO_LARGE);
			ASSERT(idx + num_leds <= user_num_leds, ERR_INDEX_TOO_LARGE);
			while(num_leds--) {
				set_led_rgb(idx, data[color_idx], data[color_idx + 1], data[color_idx + 2]);
				color_idx += 3;
				idx += 1;
			}
			FastLED.show();
			break;
		}
		case CMD_GET_PROTOCOL_VERSION:
			*resp = PROTOCOL_VERSION;
			*resp_len = 1;
			break;
		case CMD_GET_LED:
			{
				uint8_t idx = data[0];
				ASSERT(header->len == LEN_CMD_GET_LED, ERR_WRONG_PACKET_SIZE);
				ASSERT(idx < user_num_leds, ERR_INDEX_TOO_LARGE);
				resp[0] = idx;
				*resp_len = 1;
				get_led_rgb(idx, &resp[1]);
				*resp_len += 3;
				break;
			}
		case CMD_GET_LEDS:
			{
				uint8_t idx = data[0];
				uint8_t num_leds = data[1];
				ASSERT(header->len == LEN_CMD_GET_LEDS, ERR_WRONG_PACKET_SIZE);
				ASSERT(idx < user_num_leds, ERR_INDEX_TOO_LARGE);
				ASSERT(idx + num_leds <= user_num_leds, ERR_INDEX_TOO_LARGE);
				*resp++ = idx;
				*resp_len = 1;
				while(num_leds--) {
					get_led_rgb(idx++, resp);
					*resp_len += 3;
					resp += 3;
				}
				break;
			}
    case CMD_ROTATE_LEDS:
    {
      uint8_t count = data[0];
      ASSERT(header->len == LEN_CMD_ROTATE_LEDS, ERR_PACKET_TOO_SHORT);
      rotate_leds(count);
      FastLED.show();
      break;
    }
    case CMD_ROTATE_LEDS_WITH_DELAY:
    {
      uint8_t count = data[0];
      uint8_t rot_delay = data[1];
      ASSERT(header->len == LEN_CMD_ROTATE_LEDS_WITH_DELAY, ERR_PACKET_TOO_SHORT);
      while(count--) {
        rotate_leds(1);
        FastLED.show();
        delay(rot_delay);
      }
      break;
    }
		default:
			FAIL(ERR_UNKNOWN_COMMAND);
	}
error_case:
	return status;
}

static inline void comm_sync() {
	while(Serial.read() != SOP_MARKER) { }
}

static inline uint8_t comm_receive(struct comm_header * header, uint8_t * data) {
	uint8_t status = STATUS_OK;
	int n;
	n = Serial.readBytes((uint8_t *)header, sizeof(*header));
	ASSERT(n == sizeof(*header), ERR_FAILED_TO_READ_HEADER);
	ASSERT(header->len <= MAX_DATA_SIZE, ERR_PACKET_TOO_LONG);
	if (header->len) {
		n = Serial.readBytes(data, header->len);
		ASSERT(n == header->len, ERR_FAILED_TO_READ_PACKET);
	}
error_case:
	return status;
}

static inline void comm_valid_response(struct comm_header * header, uint8_t * data, uint8_t data_len) {
	struct comm_response_header resp;
	resp.header.command = RESPONSE_COMMAND(header->command);
	resp.header.len = data_len + 1;
	resp.status = STATUS_OK;
	Serial.write((uint8_t *)&resp, COMM_RESP_HEADER_SIZE);
	if (data_len) {
		Serial.write(data, data_len);
	}
}

static inline void comm_error_response(struct comm_header * header, uint8_t status) {
	struct comm_response_header resp;
	resp.header.command = RESPONSE_COMMAND(header->command);
	resp.header.len = 1;
	resp.status = status;
	set_led_rgb(status % LED_COUNT, 0x00, 0x00, 0x80);
	Serial.write((uint8_t *)&resp, COMM_RESP_HEADER_SIZE);
}

void loop()
{
	int n;
	uint8_t resp[MAX_DATA_SIZE];
	uint8_t resp_len;
	uint8_t status = STATUS_OK;
	struct comm_header header = {
		CMD_INVALID,
		0
	};
	uint8_t data[MAX_DATA_SIZE];

	comm_sync();

	status = comm_receive(&header, data);
	ASSERT(status == STATUS_OK, status);

	status = handle_command(&header, data, resp, &resp_len);
	ASSERT(status == STATUS_OK, status);

	comm_valid_response(&header, resp, resp_len);
	return;

error_case:
	comm_error_response(&header, status);
	return;	
}
