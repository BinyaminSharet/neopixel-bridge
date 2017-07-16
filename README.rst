Neopixel Bridge
===============

Control Neopixels over USB serial.

Firmware
--------

Arduino program that accepts commands from serial and sets the pixels accordingly.

Currently I use it for a 16-pixel ring, but this can be changed in the header file
(firmware/neopixel_bridge.h)

Client
------

Python2.7 class that implements the control protocol over serial
(client/neopixel_bridge.py)

client/bridge_examples.py is a small example program that uses the bridge.


Protocol
--------

Command structure:

+--------------+-----------------------------+
| byte         | Description                 |
+==============+=============================+
| 0            | opcode                      |
+--------------+-----------------------------+
| 1            | data length                 |
+--------------+-----------------------------+
| 2 .. len + 2 | data                        |
+--------------+-----------------------------+

Response structure:

+--------------+-----------------------------+
| byte         | Description                 |
+==============+=============================+
| 0            | opcode                      |
+--------------+-----------------------------+
| 1            | data length                 |
+--------------+-----------------------------+
| 2            | status                      |
+--------------+-----------------------------+
| 3 .. len + 2 | data                        |
+--------------+-----------------------------+
