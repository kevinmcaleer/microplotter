# In stepper.py
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
    
    def __init__(self, in1, in2, in3, in4, delay_us=1500, mode='full', endstop_pin=None, endstop_direction=1):
        from machine import Pin

        self.coils = [Pin(in1, Pin.OUT), Pin(in2, Pin.OUT), Pin(in3, Pin.OUT), Pin(in4, Pin.OUT)]
        self.delay_us = delay_us
        self.endstop = Pin(endstop_pin, Pin.IN, Pin.PULL_UP) if endstop_pin is not None else None
        self.set_step_mode(mode)
        self.delay_us = delay_us
        self.end_stop_direction = endstop_direction

    def set_step_mode(self, mode):
        if mode == "full":
            self.step_sequence = self.full_sequence
            print("Setting mode to Full Sequence")
        else:
            self.step_sequence = self.half_sequence
            print("Setting mode to Half Sequence")
        print(f"Mode: {self.step_sequence}")

    def move(self, steps, direction=1):
        seq = self.step_sequence if direction > 0 else self.step_sequence[::-1]

        for _ in range(int(steps)):
            # Only stop if moving in the end_stop_direction AND the endstop is triggered
            if self.endstop and self.end_stop_direction == direction and self.endstop.value():
                print("Endstop triggered — stopping movement")
                self.stop()
                break

            for step in seq:
                self.set_step(step)
                try:
                    sleep_us(self.delay_us)
                except Exception as e:
                    print(f"Error during sleep: {e}")
        self.stop()


    def stop(self):
        self.set_step((0, 0, 0, 0))

    def set_step(self, step):
        for i, coil in enumerate(self.coils):
            coil.value(step[i])

    def is_endstop_triggered(self):
        return self.endstop.value() if self.endstop else False