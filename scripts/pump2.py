import RPi.GPIO as GPIO
import time

# ================================
#   KONFIGURATION
# ================================

# BCM-PINs für die Relais-Kanäle
# → diese GPIOs gehen auf IN1, IN2, IN3 des Relaismoduls
PIN_PUMP_1 = 17    # Beispiel: IN1


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

GPIO.setup(17, GPIO.OUT)
GPIO.output(17, RELAY_INACTIVE_STATE)

# ================================
#   TEST / DEMO
# ================================

if __name__ == "__main__":
    try:
        print("Starte Pumpen-Test...")

        # Beispiel: Pumpe 1 für 3 Sekunden an
        GPIO.output(17, RELAY_ACTIVE_STATE)
        time.sleep(300)
        GPIO.output(17, RELAY_INACTIVE_STATE)
        time.sleep(1)

        print("Test beendet.")

    except KeyboardInterrupt:
        print("\nAbgebrochen mit STRG+C.")
    finally:
        print("Schalte alle Pumpen aus & clean up...")
        GPIO.output(17, RELAY_INACTIVE_STATE)
        GPIO.cleanup()
        print("GPIO cleaned up.")
