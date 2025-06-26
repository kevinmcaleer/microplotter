# Homing test

from stepper import StepperMotor

pen = StepperMotor(8,9,10,11, mode="full")

def pen_up():
    pen.move(90,direction=-1)
    print(f"up, direction=-1")
    
def pen_down():
    pen.move(90,direction=1)
    print(f"down, direction=1")

x = StepperMotor(0,1,2,3,delay_us=1500,mode='full',endstop_pin=16, endstop_direction=1)
y = StepperMotor(4,5,6,7,delay_us=1500,mode='full',endstop_pin=15, endstop_direction=-1)
for step in range(0,800):
    x.move(1,direction=-1)
    y.move(1,direction=-1)
    if step in [100,400,600,799]:
        pen_down()
    if step in [200,500,700,800]:
        pen_up()
    
x.stop()
y.stop()
