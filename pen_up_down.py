# Pen up/down

from stepper import StepperMotor
from time import sleep

DELAY = 10000

pen = StepperMotor(8,9,10,11)
pen.delay_us = DELAY

def pen_up(pen):
    print("pen up")
    pen.move(steps=90, direction=-1)
    
def pen_down(pen):
    print("pen down")
    pen.move(steps=90, direction=1)

pen_down(pen)
sleep(1)
pen_up(pen)
sleep(1)