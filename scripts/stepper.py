#######################################
# Auf dem PI:
# sudo pip3 install rpimotorlib
#######################################
import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib
import time

direction = #DIRECTIONPIN
step = #STEP GPIO PIN
EN_PIN = #ENABLE PIN (LOW TO ENABLE)

mymotortest = RpiMotorLib."Modell.Motorname (z.B.A4988Nema)"(direction, step, (21,21,21), "DRV2209")
GPIO.setup(EN_pin,GPIO.OUT)

GPIO.output(EN_pin,GPIO.LOW)     #enable zu low um Motor zu enablen
mymotortest.motor_go(False,      #True=Clockwise, False=Counter-Clockwise
                     "Full" ,    #Schritt type (Full,Half,1/4,1/8,1/16,1/32)
                     200,        #Anzahl Schritte
                     .0005,      #Schritt Verzögerung
                     False,      #True = print verbose output
                     .05)        #initiale Verzögerung [sek]

GPIO.cleanup()
