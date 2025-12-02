import RPi.GPIO as GPIO
import time

# =====================================
# PIN-KONFIGURATION
# =====================================

PIN_STEP = 17
PIN_DIR = 27
PIN_EN = 22

STEP_DELAY = 0.0005  # kann langsamer gestellt werden (z.B. 0.001)

# =====================================

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(PIN_STEP, GPIO.OUT)
GPIO.setup(PIN_DIR, GPIO.OUT)
GPIO.setup(PIN_EN, GPIO.OUT)

GPIO.output(PIN_EN, GPIO.LOW)  # Motor aktiv
GPIO.output(PIN_DIR, GPIO.HIGH)  # Richtung egal für Test


def test_steps(max_steps=20000):
    """
    Gibt Schritt für Schritt Impulse aus und zählt mit.
    Stoppe das Script (STRG+C), sobald der Motor genau 1 cm gefahren ist.
    """

    print("Starte Step-Test…")
    print("→ Stoppe mit STRG+C, wenn der Motor 1 cm gefahren ist.")
    print("→ Anschließend steht die Schrittzahl im Terminal.\n")

    step_count = 0

    try:
        while step_count < max_steps:
            GPIO.output(PIN_STEP, GPIO.HIGH)
            time.sleep(STEP_DELAY)
            GPIO.output(PIN_STEP, GPIO.LOW)
            time.sleep(STEP_DELAY)

            step_count += 1

            # alle 50 Steps ausgeben (sonst spammt das Terminal)
            if step_count % 50 == 0:
                print(f"Steps bisher: {step_count}")

    except KeyboardInterrupt:
        print("\n\n--- ABGEBROCHEN ---")
        print(f"Schritte bis zum STOP: {step_count}")
        print("→ Diese Schrittzahl entspricht deiner realen Bewegung.")

    finally:
        GPIO.output(PIN_EN, GPIO.HIGH)
        GPIO.cleanup()
        print("GPIO cleaned up.")


if __name__ == "__main__":
    test_steps()
