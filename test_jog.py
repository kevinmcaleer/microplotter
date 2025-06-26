# test pen
from stepper import StepperMotor

pen = StepperMotor(8,9,10,11, mode="full")

while True:
    key_in = input("jog")
    if key_in == "d":
        pen.move(10,direction=1)
        print(f"down, direction=1")
    if key_in == "a":
        pen.move(10,direction=-1)
        print(f"up, direction=1")