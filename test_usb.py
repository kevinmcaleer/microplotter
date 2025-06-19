from time import sleep
import sys

# Assume StepperMotor and GCodeInterpreter classes are already defined

motor_x = StepperMotor(14, 15, 18, 23)
motor_y = StepperMotor(2, 3, 4, 5)
motor_z = StepperMotor(6, 7, 8, 9)

gcode = GCodeInterpreter(motor_x, motor_y, motor_z)

print("Waiting for G-code over USB...")

while True:
    try:
        line = sys.stdin.readline()  # Read from USB
        if line:
            print("Received:", line)
            gcode.parse_line(line)
    except Exception as e:
        print("Error:", e)
