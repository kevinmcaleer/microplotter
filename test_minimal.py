import time
import usb_cdc

serial = usb_cdc.data

# Wait until the USB serial is connected
print("Waiting for USB serial connection...")
while not serial.connected:
    time.sleep(0.1)

# Now USB is connected — this message will be visible
print("✅ USB connected!")
serial.write(b"Grbl 1.1f ['$' for help]\r\n")