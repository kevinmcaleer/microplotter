# main.py - CircuitPython GRBL-compatible interpreter for UGS

import time

import usb_cdc
from stepper import StepperMotor
from gcode_interpreter import GCodeInterpreter

# Initialize stepper motors
motor_x = StepperMotor(14, 15, 18, 23)
motor_y = StepperMotor(2, 3, 4, 5)
motor_z = StepperMotor(6, 7, 8, 9)
gcode = GCodeInterpreter(motor_x, motor_y, motor_z)

STEPS_PER_MM = 10  # Tune to your mechanical setup
serial = usb_cdc.data

banner_sent = False
last_status = time.monotonic()

while True:
    try:
        # Wait for USB connection
        if not serial.connected:
            banner_sent = False
            time.sleep(0.1)
            continue

        # Send banner on first message
        if not banner_sent and serial.in_waiting:
            serial.write(b"Grbl 1.1f ['$' for help]\r\n")
            serial.write(b"<Idle|MPos:0.000,0.000,0.000|FS:0,0>\r\n")
            serial.write(b"[MSG:'$H'|'$X' to unlock]\r\n")
            pos = gcode.position
            for _ in range(3):
                serial.write("<Idle|MPos:{:.3f},{:.3f},{:.3f}|FS:0,0>\r\n".format(
                    pos['X'], pos['Y'], pos['Z']).encode())
            banner_sent = True

        # Periodic status every 2s
        if time.monotonic() - last_status > 2:
            pos = gcode.position
            serial.write("<Idle|MPos:{:.3f},{:.3f},{:.3f}|FS:0,0>\r\n".format(
                pos['X'], pos['Y'], pos['Z']).encode())
            last_status = time.monotonic()

        if serial.in_waiting:
            line = serial.readline().decode().strip("\r\n")
            if not line:
                continue

            if line == '\x18':  # Soft reset (Ctrl-X / 0x18)
                banner_sent = False
                continue

            if line == '?':
                pos = gcode.position
                serial.write("<Idle|MPos:{:.3f},{:.3f},{:.3f}|FS:0,0>\r\n".format(
                    pos['X'], pos['Y'], pos['Z']).encode())

            elif line == '$I':
                serial.write(b"[VER:MicroPythonGRBL:1.1]\r\n")
                serial.write(b"[OPT:CPY,USB,3AXIS]\r\n")
                serial.write(b"ok\r\n")

            elif line == '$X':
                serial.write(b"ok\r\n")

            elif line == '$':
                serial.write(b"$$=not_implemented\r\n")
                serial.write(b"ok\r\n")

            elif line == '$G':
                serial.write(b"[G91 G21 G94]\r\n")
                serial.write(b"ok\r\n")

            elif line.startswith('G92'):
                new_pos = {}
                for token in line.split()[1:]:
                    axis = token[0]
                    value = float(token[1:])
                    if axis in 'XYZ':
                        new_pos[axis] = value
                gcode.set_position(**new_pos)
                serial.write(b"ok\r\n")

            elif line.startswith('$J='):
                jog_cmd = line[3:].strip()
                if not jog_cmd.startswith("G91"):
                    serial.write(b"error: Only G91 (relative) jogs supported\r\n")
                else:
                    dx = dy = dz = 0
                    for token in jog_cmd.split():
                        if token.startswith('X'):
                            dx = float(token[1:]) * STEPS_PER_MM
                        elif token.startswith('Y'):
                            dy = float(token[1:]) * STEPS_PER_MM
                        elif token.startswith('Z'):
                            dz = float(token[1:]) * STEPS_PER_MM
                    gcode.jog(dx, dy, dz)
                    serial.write(b"ok\r\n")

            else:
                gcode.parse_line(line)
                serial.write(b"ok\r\n")

    except Exception as e:
        serial.write("error: {}\r\n".format(str(e)).encode())