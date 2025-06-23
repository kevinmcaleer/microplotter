from machine import Pin
from time import sleep_us

class StepperMotor:
    full_sequence = [
        (1, 1, 0, 0),
        (0, 1, 1, 0),
        (0, 0, 1, 1),
        (1, 0, 0, 1)
    ]

    half_sequence = [
        (1, 0, 0, 0),
        (1, 1, 0, 0),
        (0, 1, 0, 0),
        (0, 1, 1, 0),
        (0, 0, 1, 0),
        (0, 0, 1, 1),
        (0, 0, 0, 1),
        (1, 0, 0, 1)
    ]

    def __init__(self, in1, in2, in3, in4, delay_us=1500, mode='full'):
        self.coils = [
            Pin(in1, Pin.OUT),
            Pin(in2, Pin.OUT),
            Pin(in3, Pin.OUT),
            Pin(in4, Pin.OUT)
        ]
        self.delay_us = delay_us
        self.set_step_mode(mode)

    def set_step_mode(self, mode):
        """Set stepping mode: 'full' or 'half'"""
        if mode == 'full':
            self.step_sequence = self.full_sequence
        elif mode == 'half':
            self.step_sequence = self.half_sequence
        else:
            raise ValueError("Invalid mode. Use 'full' or 'half'.")

    def set_step(self, step):
        for i, coil in enumerate(self.coils):
            coil.value(step[i])

    def move(self, steps, direction=1):
        seq = self.step_sequence if direction > 0 else self.step_sequence[::-1]
        for _ in range(int(steps)):
            for step in seq:
                self.set_step(step)
                sleep_us(self.delay_us)

    def stop(self):
        self.set_step((0, 0, 0, 0))
