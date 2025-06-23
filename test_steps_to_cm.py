from stepper import StepperMotor

# Setup motors

y_motor = StepperMotor(4,5,6,7)
x_motor = StepperMotor(0,1,2,3)
pen_motor = StepperMotor(8,9,10,11)
# 
# 
# for step in range(0,1000): # 1000 steps = 9cm
#     y_motor.move(steps=1, direction=-1)
# 
#     print(f"step {step}")
    
x_motor.stop()    
y_motor.stop()
pen_motor.stop()
