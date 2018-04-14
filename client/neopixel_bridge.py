#!/usr/bin/env python
import serial
import struct
import time


SOP_MARKER = 0xfd

CMD_GET_MAX_LEDS = 0
CMD_SET_NUM_LEDS = 1
CMD_SET_LED = 2
CMD_SET_LEDS = 3
CMD_GET_PROTOCOL_VERSION = 4
CMD_GET_LED = 5
CMD_GET_LEDS = 6
CMD_INVALID = 0x7f

RESPONSE_CMD_FLAG = 0x80

CURRENT_PROTOCOL_VERSION = 2


class NeopixelBridge(object):

    def __init__(self, port):
        self._serial = serial.Serial(port, 115200)
        wait = 2
        print 'waiting for arduino to initialize (%s seconds)' % wait
        time.sleep(wait)

    def do_command(self, cmd, data=None):
        if data is None:
            data = []
        buff = struct.pack('BBB', SOP_MARKER, cmd, len(data))
        if data:
            buff += ''.join(chr(x) for x in data)
        # print('>> %s' % (buff.encode('hex')))
        self._serial.write(buff)
        resp_header = self._serial.read(3)
        resp_cmd, resp_len, resp_code = struct.unpack('BBB', resp_header)
        # print('<< %s' % (resp_header.encode('hex')))
        if resp_code != 0:
            raise Exception('Command %#02x failed with response %#02x' % (cmd, resp_code))
        if resp_len > 1:
            resp_data = self._serial.read(resp_len - 1)
            # print('<< %s' % (resp_data.encode('hex')))
        else:
            resp_data = None
        return resp_data

    def get_max_leds(self):
        resp_data = self.do_command(CMD_GET_MAX_LEDS)
        return struct.unpack('B', resp_data)[0]

    def set_num_leds(self, n):
        self.do_command(CMD_SET_NUM_LEDS, [n])

    def set_led(self, idx, r, g, b):
        self.do_command(CMD_SET_LED, [idx, r, g, b])

    def set_leds(self, idx, rgb_list):
        '''
        set values of leds from a given index

        :param idx: index of first led to set
        :param rgb_list: list of rgb tuples
        '''
        # flatten rgb_list
        rgbs = [x for rgb in rgb_list for x in rgb]
        self.do_command(CMD_SET_LEDS, [idx] + rgbs)

    def get_protocol_version(self):
        resp_data = self.do_command(CMD_GET_PROTOCOL_VERSION)
        return struct.unpack('B', resp_data)[0]

    def get_led(self, idx):
        '''
        get the RGB values of a led
        :param idx: index of led
        :return: (r, g, b) tuple
        '''
        resp_data = self.do_command(CMD_GET_LED, [idx])
        return struct.unpack('BBB', resp_data[1:])

    def get_leds(self, idx, count):
        '''
        get the RGB values of a led sequence
        :param idx: starting index of the led sequence
        :return: list of (r, g, b) tuples
        '''
        resp_data = self.do_command(CMD_GET_LEDS, [idx, count])
        # recvd_idx = struct.unpack('B', resp_data[:1])[0]
        rgbs = []
        for i in range(1, len(resp_data), 3):
            rgbs.append(struct.unpack('BBB', resp_data[i:i + 3]))
        return rgbs
