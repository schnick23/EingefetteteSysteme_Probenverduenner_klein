import RPi.GPIO as GPIO
import time

# =====================================
# PIN-KONFIGURATION
# =====================================

PIN_STEP = 17
PIN_DIR  = 27
PIN_EN   = 22
PIN_ENDSTOP = 6

STEP_DELAY = 0.0005   # langsamer = sicherer für Homing

# =====================================
# GPIO SETUP
# =====================================

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(PIN_STEP, GPIO.OUT)
GPIO.setup(PIN_DIR, GPIO.OUT)
GPIO.setup(PIN_EN, GPIO.OUT)

# Endschalter mit Pull-Up
GPIO.setup(PIN_ENDSTOP, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Motor aktivieren
GPIO.output(PIN_EN, GPIO.LOW)

# Richtung: nach unten (ggf. HIGH/LOW tauschen)
GPIO.output(PIN_DIR, GPIO.LOW)

# =====================================
# HOMING-FUNKTION
# =====================================

def homing(max_steps=20000):
    """
    Fährt den Motor nach unten,
    bis der Endschalter (GPIO 6) auslöst.
    """

    print("Starte Homing...")
    print("Fahre nach unten bis Endschalter erreicht ist.\n")

    steps = 0

    try:
        while steps < max_steps:

            # Endschalter prüfen
            if GPIO.input(PIN_ENDSTOP) == GPIO.LOW:
                print("\nEndschalter ausgelöst!")
                print(f"Homing abgeschlossen nach {steps} Schritten.")
                break

            # Step-Impuls
            GPIO.output(PIN_STEP, GPIO.HIGH)
            time.sleep(STEP_DELAY)
            GPIO.output(PIN_STEP, GPIO.LOW)
            time.sleep(STEP_DELAY)

            steps += 1

            if steps % 200 == 0:
                print(f"Steps: {steps}")

        else:
            print("\nWARNUNG: Maximalzahl an Schritten erreicht!")
            print("Endschalter wurde NICHT gefunden.")

    finally:
        GPIO.output(PIN_EN, GPIO.HIGH)
        GPIO.cleanup()
        print("GPIO cleaned up.")


# =====================================
# MAIN
# =====================================

if __name__ == "__main__":
    homing()
