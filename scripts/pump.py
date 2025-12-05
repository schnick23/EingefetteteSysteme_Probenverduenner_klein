import RPi.GPIO as GPIO
import time

# ================================
#   KONFIGURATION
# ================================

# BCM-PINs für die Relais-Kanäle
# → diese GPIOs gehen auf IN1, IN2, IN3 des Relaismoduls
PIN_PUMP_1 = 17    # Beispiel: IN1
#PIN_PUMP_2 = 6    # Beispiel: IN2
#PIN_PUMP_3 = 13   # Beispiel: IN3

PUMP_PINS = {
    1: PIN_PUMP_1,
    #2: PIN_PUMP_2,
    #3: PIN_PUMP_3,
}

# Viele 8-Kanal-Relais sind "active LOW":
#   LOW  = Relais zieht an → Verbraucher AN
#   HIGH = Relais aus      → Verbraucher AUS
RELAY_ACTIVE_STATE = GPIO.HIGH
RELAY_INACTIVE_STATE = GPIO.LOW	

# ================================
#   SETUP
# ================================

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

for pin in PUMP_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
    # Standard: alle Pumpen aus
    GPIO.output(pin, RELAY_INACTIVE_STATE)


# ================================
#   FUNKTIONEN
# ================================

def pump_on(pump_id: int):
    """
    Schaltet die angegebene Pumpe EIN.
    pump_id: 1, 2 oder 3
    """
    if pump_id not in PUMP_PINS:
        raise ValueError(f"Ungültige Pumpen-ID {pump_id}. Erlaubt: {list(PUMP_PINS.keys())}")

    pin = PUMP_PINS[pump_id]
    GPIO.output(pin, RELAY_ACTIVE_STATE)
    print(f"Pumpe {pump_id} EIN (Pin {pin})")


def pump_off(pump_id: int):
    """
    Schaltet die angegebene Pumpe AUS.
    """
    if pump_id not in PUMP_PINS:
        raise ValueError(f"Ungültige Pumpen-ID {pump_id}. Erlaubt: {list(PUMP_PINS.keys())}")

    pin = PUMP_PINS[pump_id]
    GPIO.output(pin, RELAY_INACTIVE_STATE)
    print(f"Pumpe {pump_id} AUS (Pin {pin})")


def pump_for_seconds(pump_id: int, seconds: float):
    """
    Schaltet eine Pumpe für eine bestimmte Zeit ein und dann wieder aus.
    """
    print(f"Pumpe {pump_id} für {seconds} Sekunden einschalten...")
    pump_on(pump_id)
    time.sleep(seconds)
    pump_off(pump_id)
    print(f"Pumpe {pump_id} wieder aus.")


def all_pumps_off():
    """
    Sicherheitshalber alle Pumpen ausschalten.
    """
    for pid in PUMP_PINS:
        pump_off(pid)


# ================================
#   TEST / DEMO
# ================================

if __name__ == "__main__":
    try:
        print("Starte Pumpen-Test...")

        # Beispiel: Pumpe 1 für 3 Sekunden an
        pump_for_seconds(1, 3)
        time.sleep(1)

        # Beispiel: Pumpe 2 für 2 Sekunden an
        #pump_for_seconds(2, 2)
        #time.sleep(1)

        # Beispiel: Pumpe 3 bleibt 5 Sekunden an, dann manuell aus
        #pump_on(3)
        #print("Pumpe 3 ist jetzt an für 5 Sekunden...")
        #time.sleep(5)
        #pump_off(3)

        print("Test beendet.")

    except KeyboardInterrupt:
        print("\nAbgebrochen mit STRG+C.")
    finally:
        print("Schalte alle Pumpen aus & clean up...")
        all_pumps_off()
        GPIO.cleanup()
        print("GPIO cleaned up.")
