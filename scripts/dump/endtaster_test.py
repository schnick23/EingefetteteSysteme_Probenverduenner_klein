import RPi.GPIO as GPIO
import time



GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    try:
        print(GPIO.input(26))
        time.sleep(0.1)
    except KeyboardInterrupt:
        GPIO.cleanup()
        break