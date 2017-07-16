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


programs = {}


def program(cmd, desc, possible_args=''):
    def program_wrap(func):
        def func_wrap(*args, **kwargs):
            return func(*args, **kwargs)
        programs[cmd] = (func, desc, possible_args)
        return func_wrap
    return program_wrap


@program('off', 'tun all leds off')
def prog_leds_off(bridge, args):
    num_leds = bridge.get_max_leds()
    if not num_leds:
        print('Failed to get number of leds')
    else:
        for i in range(num_leds):
            bridge.set_led(i, 0, 0, 0)


@program('rainbow', 'show a rainbow', 'rotate=x')
def prog_show_rainbow(bridge, args):
    num_leds = bridge.get_max_leds()
    if not num_leds:
        print('Failed to get number of leds')
    else:
        base = []
        for i in range(num_leds):
            r, g, b = colorsys.hsv_to_rgb((1.0 / num_leds) * i, 1, 0.2)
            base.append((int(r * 255), int(g * 255), int(b * 255)))

        n = int(args.get('rotate', 0)) * num_leds + 1

        for rounds in range(n):
            bridge.set_leds(0, base)
            base = base[-1:] + base[:-1]
            if (rounds < (n - 1)):
                time.sleep(0.1)


def run_program(device, program, args):
    if program not in programs:
        print('Invalid program selected: %s' % (program))
        print('Select one of: %s' % (','.join(sorted(programs.keys()))))
        return
    try:
        bridge = NeopixelBridge(device)
        p_func, p_desc, _ = programs[program]
        print('Running program %s - %s' % (program, p_desc))
        p_func(bridge, args)
    except Exception as ex:
        print('Caught exception: %s' % ex)


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
