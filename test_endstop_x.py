# end stop test

from machine import Pin
from time import sleep

a = Pin(12, Pin.IN, Pin.PULL_UP)
b = Pin(16, Pin.IN, Pin.PULL_UP)

count = 0

while True:
    if a.value() == 1:
        print(f"button a pressed, {count}")
    
    if b.value() == 1:
        print(f"button b pressed", {count})
    count += 1
    sleep(0.01)
    
    
