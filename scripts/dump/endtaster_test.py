import RPi.GPIO as GPIO
import time




GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while true:
    print(GPIO.input(26))
    time.sleep(0.1)