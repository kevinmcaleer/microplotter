# jog X left

from stepper import StepperMotor

motor_x = StepperMotor(0, 1, 2, 3, endstop_pin=16, endstop_direction=1)

motor_x.move(100,direction=1)
motor_x.stop()