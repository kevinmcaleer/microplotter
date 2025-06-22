from machine import Pin
from time import sleep_us

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

    def __init__(self, in1, in2, in3, in4, delay_us=1500):
        self.coils = [
            Pin(in1, Pin.OUT),
            Pin(in2, Pin.OUT),
            Pin(in3, Pin.OUT),
            Pin(in4, Pin.OUT)
        ]
        self.delay_us = delay_us

    def set_step(self, step):
        for i, coil in enumerate(self.coils):
            coil.value(step[i])

    def move(self, steps, direction=1):
        seq = self.step_sequence if direction > 0 else self.step_sequence[::-1]
        for _ in range(int(steps)):
            for step in seq:
                self.set_step(step)
                sleep_us(self.delay_us)  # precise microsecond timing

    def stop(self):
        self.set_step((0, 0, 0, 0))
