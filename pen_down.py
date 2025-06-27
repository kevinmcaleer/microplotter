# test jog
from stepper import StepperMotor
from time import sleep

pen = StepperMotor(8,9,10,11, mode="full")

def pen_up():
    pen.move(45,direction=-1)
    print(f"up, direction=-1")
    
def pen_down():
    pen.move(45,direction=1)
    print(f"down, direction=1")
    
# pen_up()
# sleep(2)
pen_down()
# sleep(2)
# pen_up()

