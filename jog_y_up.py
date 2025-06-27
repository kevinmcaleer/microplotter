# jog Y UP

from stepper import StepperMotor

motor_y = StepperMotor(4, 5, 6, 7, endstop_pin=15, endstop_direction=-1)

motor_y.move(100,direction=-1)
