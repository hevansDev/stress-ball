from machine import ADC, Pin
import time

FORCE_SENSOR_PIN = 28
force_sensor = ADC(Pin(FORCE_SENSOR_PIN))

while True:
    analog_reading = force_sensor.read_u16()
    analog_reading = analog_reading // 64
    
    # This automatically sends over USB to your laptop
    print(f"{analog_reading}")
    
    time.sleep(0.1)  # Send 10 times per second

