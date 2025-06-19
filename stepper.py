from machine import Pin
from time import sleep

class StepperMotor:
    step_sequence = [
        (1, 0, 0, 0),
        (1, 1, 0, 0),
        (0, 1, 0, 0),
        (0, 1, 1, 0),
        (0, 0, 1, 0),
        (0, 0, 1, 1),
        (0, 0, 0, 1),
        (1, 0, 0, 1)
    ]

    def __init__(self, in1, in2, in3, in4, speed=0.0005):
        self.coil_a_1 = Pin(in1, Pin.OUT)
        self.coil_a_2 = Pin(in2, Pin.OUT)
        self.coil_b_1 = Pin(in3, Pin.OUT)
        self.coil_b_2 = Pin(in4, Pin.OUT)
        self.speed = speed

    def set_step(self, w1, w2, w3, w4):
        self.coil_a_1.value(w1)
        self.coil_a_2.value(w2)
        self.coil_b_1.value(w3)
        self.coil_b_2.value(w4)

    def move(self, steps, direction=1):
        sequence = self.step_sequence[::-1] if direction == -1 else self.step_sequence
        for _ in range(steps):
            for step in sequence:
                self.set_step(*step)
                sleep(self.speed)

    def stop(self):
        self.set_step(0, 0, 0, 0)
