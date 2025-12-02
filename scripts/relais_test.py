from gpiozero import DigitalOutputDevice
from time import sleep

# Ersetzen Sie 4 durch die GPIO-Nummer, mit der das Relais verbunden ist
RELAIS_PIN = 4 

# Initialisierung des GPIO-Pins als digitaler Ausgang
relais = DigitalOutputDevice(RELAIS_PIN)

print("Relais wird eingeschaltet...")
relais.on() # Relais einschalten (GPIO HIGH)
sleep(3)   # 3 Sekunden warten

print("Relais wird ausgeschaltet...")
relais.off() # Relais ausschalten (GPIO LOW)
