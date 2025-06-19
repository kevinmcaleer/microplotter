from stepper import StepperMotor

SPEED = 0.001

x_motor = StepperMotor(0,1,2,3)
y_motor = StepperMotor(4,5,6,7)
pen_motor = StepperMotor(8,9,10,11)

x_motor.speed = SPEED
y_motor.speed = SPEED
pen_motor.speed = SPEED

x_motor.move(steps=100, direction=-1)
y_motor.move(steps=100, direction=-1)
pen_motor.move(steps=100, direction=1)