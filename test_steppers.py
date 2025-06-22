from stepper import StepperMotor

# Setup motors
x_motor = StepperMotor(0,1,2,3)
y_motor = StepperMotor(4,5,6,7)
pen_motor = StepperMotor(8,9,10,11)

for step in range(0,1000):
    x_motor.move(steps=1, direction=1)
    y_motor.move(steps=1, direction=1)
    pen_motor.move(steps=1, direction=-1)
    print(f"step {step}")