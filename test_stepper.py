from stepper import StepperMotor
from time import sleep

s = StepperMotor(0,1, 2, 3, endstop_pin=12, mode='full')

for step in range(0,10000):
    if s.is_endstop_triggered():
        print("Origin found")
        break
  
    print(f'step: {step} end stop - {s.is_endstop_triggered()}')
    s.move(steps=1,direction=1)
#     sleep(0.1)