from time import sleep, ticks_ms, ticks_diff
from stepper import StepperMotor
from gcode_interpreter import GCodeInterpreter
import sys
import os

# Disable REPL on USB to avoid collisions
os.dupterm(None, 0)

# Initialize stepper motors
motor_x = StepperMotor(14, 15, 18, 23)
motor_y = StepperMotor(2, 3, 4, 5)
motor_z = StepperMotor(6, 7, 8, 9)
gcode = GCodeInterpreter(motor_x, motor_y, motor_z)

STEPS_PER_MM = 10  # Tune to your mechanical setup

# GRBL startup banner
sys.stdout.write("Grbl 1.1f ['$' for help]\r\n")
sleep(0.1)
sys.stdout.write("[MSG:'$H'|'$X' to unlock]\r\n")  # NEW
sys.stdout.write("<Idle|MPos:0.000,0.000,0.000|FS:0,0>\r\n")

# Send a few initial status reports to satisfy UGS
for _ in range(3):
    pos = gcode.position
    sys.stdout.write("<Idle|MPos:{:.3f},{:.3f},{:.3f}|FS:0,0>\r\n".format(
        pos['X'], pos['Y'], pos['Z']
    ))
    sleep(0.05)

last_status = ticks_ms()

while True:
    try:
        # Send status update every 2s
        sys.stdout.write("<Idle|time now{}, last_status{}".format(ticks_ms(),last_status))
        if ticks_diff(ticks_ms(), last_status) > 2000:
            pos = gcode.position
            sys.stdout.write("<Idle|MPos:{:.3f},{:.3f},{:.3f}|FS:0,0>\r\n".format(
                pos['X'], pos['Y'], pos['Z']
            ))
            last_status = ticks_ms()

        line = sys.stdin.readline()
        if not line:
            continue
        line = line.strip()

        if line == '?':
            pos = gcode.position
            sys.stdout.write("<Idle|MPos:{:.3f},{:.3f},{:.3f}|FS:0,0>\r\n".format(
                pos['X'], pos['Y'], pos['Z']
            ))

        elif line == '$I':
            sys.stdout.write("[VER:MicroPythonGRBL:1.1]\r\n")
            sys.stdout.write("[OPT:MPY,USB,3AXIS]\r\n")
            sys.stdout.write("ok\r\n")

        elif line == '$X':
            sys.stdout.write("ok\r\n")

        elif line == '$':
            sys.stdout.write("$$=not_implemented\r\n")
            sys.stdout.write("ok\r\n")

        elif line == '$G':
            sys.stdout.write("[G91 G21 G94]\r\n")
            sys.stdout.write("ok\r\n")

        elif line.startswith('G92'):
            new_pos = {}
            for token in line.split()[1:]:
                axis = token[0]
                value = float(token[1:])
                if axis in 'XYZ':
                    new_pos[axis] = value
            gcode.set_position(**new_pos)
            sys.stdout.write("ok\r\n")

        elif line.startswith('$J='):
            jog_cmd = line[3:].strip()
            if not jog_cmd.startswith("G91"):
                sys.stdout.write("error: Only G91 (relative) jogs supported\r\n")
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
                sys.stdout.write("ok\r\n")

        else:
            gcode.parse_line(line)
            sys.stdout.write("ok\r\n")

    except Exception as e:
        sys.stdout.write("error: {}\r\n".format(str(e)))
