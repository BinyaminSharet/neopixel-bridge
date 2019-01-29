#!/usr/bin/env python
'''
Example program for using the bridge

Usage:
    bridge_examples.py --device=<device> --program=<program> [--args=<args>]
    bridge_examples.py --list

Options:
    -d --device=<device>    a path to the serial device
    -p --program=<pattern>  the program to run
    -a --args=<args>        comma-separated list of arguments to the program
    -l --list               list programs
'''
import colorsys
import docopt
import time
from neopixel_bridge import NeopixelBridge
from neopixel_bridge import CURRENT_PROTOCOL_VERSION


programs = {}


def program(cmd, desc, possible_args=''):
    def program_wrap(func):
        def func_wrap(*args, **kwargs):
            return func(*args, **kwargs)
        programs[cmd] = (func, desc, possible_args)
        return func_wrap
    return program_wrap


@program('off', 'turn all leds off')
def prog_leds_off(bridge, args):
    num_leds = bridge.get_max_leds()
    if not num_leds:
        print('Failed to get number of leds')
    else:
        for i in range(num_leds):
            bridge.set_led(i, 0, 0, 0)


@program('rainbow', 'show a rainbow', 'rotate=x,delay=x,value=x,num_leds=x')
def prog_show_rainbow(bridge, args):
    num_leds = bridge.get_max_leds()
    if not num_leds:
        print('Failed to get number of leds')
    else:
        base = []
        hsv_value = float(args.get('value', 0.4))
        num_leds = int(args.get('num_leds', num_leds))
        for i in range(num_leds):
            width = 1.0  # 0-1
            start_color = 0.0  # 0-1
            r, g, b = colorsys.hsv_to_rgb((width / num_leds) * i + start_color, 1, hsv_value)
            base.append((int(r * 255), int(g * 255), int(b * 255)))

        n = int(args.get('rotate', 0))
        if n:
            n = n * num_leds + 1
        delay = float(args.get('delay', 0.05))

        proto = bridge.get_protocol_version()
        has_rotate = proto >= 3
        if has_rotate:
            bridge.set_leds(0, base)
        count = 0
        while True:
            if n and (count == n):
                break
            count += 1
            if has_rotate:
                bridge.rotate_leds(1)
            else:
                bridge.set_leds(0, base)
                base = base[-1:] + base[:-1]
            if (not n) or (count < n):
                time.sleep(delay)


@program('test', 'test the APIs', 'max_leds=x')
def prog_test(bridge, args):
    print('- check protocol version')
    version = bridge.get_protocol_version()
    assert(version == CURRENT_PROTOCOL_VERSION)

    print('- check maximum number of leds')
    num_leds = bridge.get_max_leds()
    if args.get('max_leds', None):
        expected_max_leds = int(args.get('max_leds', 16))
        assert(num_leds == expected_max_leds)
    else:
        print('  max_leds was not passed, ignoring the response')

    print('- check set/get led')
    expected_rgb = (0x30, 0x00, 0x00)
    bridge.set_led(1, *expected_rgb)
    received_rgb = bridge.get_led(1)
    assert(expected_rgb == received_rgb)

    print('- check set/get leds')
    expected_rgbs = [(0x20, 0x00, 0x20), (0x30, 0x00, 0x30), (0x40, 0x00, 0x40)]
    bridge.set_leds(0, expected_rgbs)
    received_rgbs = bridge.get_leds(0, len(expected_rgb))
    assert(expected_rgbs == received_rgbs)

    print('- cleanup')
    prog_leds_off(bridge, None)


def run_program(device, program, args):
    if program not in programs:
        print('Invalid program selected: %s' % (program))
        print('Select one of: %s' % (','.join(sorted(programs.keys()))))
        return
    bridge = NeopixelBridge(device)
    p_func, p_desc, _ = programs[program]
    print('Running program %s - %s' % (program, p_desc))
    p_func(bridge, args)


def print_programs():
    for k, v in programs.iteritems():
        print('%s - %s (args: %s)' % (k, v[1], v[2]))


def build_program_arg_dict(args):
    if args:
        args = args.split(',')
    else:
        args = []
    argsdict = {}
    for arg in args:
        idx = arg.find('=')
        if idx == -1:
            argsdict[arg] = None
        else:
            argsdict[arg[:idx]] = arg[idx + 1:]
    return argsdict


def main():
    opts = docopt.docopt(__doc__)
    if opts['--list']:
        print_programs()
    elif opts['--program']:
        argsdict = build_program_arg_dict(opts['--args'])
        run_program(opts['--device'], opts['--program'], argsdict)


if __name__ == '__main__':
    main()
