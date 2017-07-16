#!/usr/bin/env python
import serial
import struct


SOP_MARKER = 0xfd

CMD_GET_MAX_LEDS = 0
CMD_SET_NUM_LEDS = 1
CMD_SET_LED = 2
CMD_SET_LEDS = 3
CMD_INVALID = 4

RESPONSE_CMD_FLAG = 0x80


class NeopixelBridge(object):

    def __init__(self, port):
        self._serial = serial.Serial(port, 115200)

    def do_command(self, cmd, data):
        buff = struct.pack('BBB', SOP_MARKER, cmd, len(data))
        if data:
            buff += ''.join(chr(x) for x in data)
        self._serial.write(buff)
        resp_header = self._serial.read(3)
        resp_cmd, resp_len, resp_code = struct.unpack('BBB', resp_header)
        if resp_len > 1:
            resp_data = self._serial.read(resp_len - 1)
        else:
            resp_data = None
        return resp_code, resp_data

    def get_max_leds(self):
        resp_code, resp_data = self.do_command(CMD_GET_MAX_LEDS, [])
        if resp_code == 0:
            # print 'Max leds: %s' % (resp_data.encode('hex'))
            return struct.unpack('B', resp_data)[0]
        else:
            print 'Got bad resp code: %#x' % (resp_code)
            return None

    def set_num_leds(self, n):
        resp_code, resp_data = self.do_command(CMD_SET_NUM_LEDS, [n])
        return resp_code

    def set_led(self, idx, r, g, b):
        resp_code, resp_data = self.do_command(CMD_SET_LED, [idx, r, g, b])
        return resp_code

    def set_leds(self, idx, rgb_list):
        '''
        set values of leds from a given index

        :param idx: index of first led to set
        :param rgb_list: list of rgb tuples
        '''
        # flatten rgb_list
        rgbs = [x for rgb in rgb_list for x in rgb]
        resp_code, resp_data = self.do_command(CMD_SET_LEDS, [idx] + rgbs)
        return resp_code
