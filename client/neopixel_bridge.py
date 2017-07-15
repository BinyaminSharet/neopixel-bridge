#!/usr/bin/env python
import serial
import struct
import colorsys


SOP_MARKER = 0xfd

CMD_GET_MAX_LEDS = 0
CMD_SET_NUM_LEDS = 1
CMD_SET_PATTERN = 2
CMD_SET_LED = 3
CMD_INVALID = 4

RESPONSE_CODE_FLAG = 0x80


class NeopixelBridge(object):

    def __init__(self, port):
        self._serial = serial.Serial(port, 115200)

    def send(self, cmd, data):
        buff = struct.pack('BBB', SOP_MARKER, cmd, len(data))
        if data:
            buff += ''.join(chr(x) for x in data)
        self._serial.write(buff)
        resp_header = self._serial.read(2)
        resp_code, resp_len = struct.unpack('BB', resp_header)
        if resp_len:
            resp_data = self._serial.read(resp_len)
        else:
            resp_data = None
        return resp_code, resp_data

    def get_max_leds(self):
        resp_code, resp_data = self.send(CMD_GET_MAX_LEDS, [])
        if resp_code == (CMD_GET_MAX_LEDS | RESPONSE_CODE_FLAG):
            # print 'Max leds: %s' % (resp_data.encode('hex'))
            return struct.unpack('B', resp_data)[0]
        else:
            print 'Got bad resp code: %#x' % (resp_code)
            return None

    def set_num_leds(self, n):
        resp_code, resp_data = self.send(CMD_SET_NUM_LEDS, [n])
        return resp_code

    def set_led(self, idx, r, g, b):
        resp_code, resp_data = self.send(CMD_SET_LED, [idx, r, g, b])
        return resp_code


if __name__ == '__main__':
    bridge = NeopixelBridge('/dev/tty.usbmodem1431')
    num_leds = bridge.get_max_leds()
    if not num_leds:
        print('Failed to get number of leds')
    else:
        step = 255 // num_leds
        for i in range(num_leds):
            # bridge.set_led(i, 0x10 * i, 0x00, 0xff - (10 * i))
            # bridge.set_led(i, 0x10 * i, 0x00, 0x00)
            r, g, b = colorsys.hsv_to_rgb((1.0 / num_leds) * i, 1, 0.1)
            bridge.set_led(i, int(r * 255), int(g * 255), int(b * 255))
            # FairyLight --> 0xFFE42D
