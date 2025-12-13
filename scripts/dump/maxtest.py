import RPi.GPIO as GPIO
import time
import sys

# =====================================
# PIN-KONFIGURATION
# =====================================
PIN_STEP = 16
PIN_DIR = 20
PIN_EN = 21

STEP_DELAY = 0.00005  # kann langsamer gestellt werden (z.B. 0.001)


def run_steps(step_count, direction):
    """
    Fährt den Motor eine bestimmte Anzahl an Schritten in der gewünschten Richtung.
    direction: "hoch" oder "runter"
    """

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(PIN_STEP, GPIO.OUT)
    GPIO.setup(PIN_DIR, GPIO.OUT)
    GPIO.setup(PIN_EN, GPIO.OUT)

    GPIO.output(PIN_EN, GPIO.LOW)  # Motor aktiv

    # Richtung setzen
    if direction.lower() in ["u","hoch","up","h","vor", "v", "forward"]:
        GPIO.output(PIN_DIR, GPIO.HIGH)
        print("Richtung: hoch")
    elif direction.lower() in ["runter", "down","d", "r", "zurueck", "z", "back", "rück"]:
        GPIO.output(PIN_DIR, GPIO.LOW)
        print("Richtung: runter")
    else:
        print("❌ Fehler: Richtung muss 'runter' oder 'hoch' sein.")
        GPIO.cleanup()
        return

    print(f"Starte Motorlauf: {step_count} Schritte\n")

    try:
        for i in range(step_count):
            GPIO.output(PIN_STEP, GPIO.HIGH)
            time.sleep(STEP_DELAY)
            GPIO.output(PIN_STEP, GPIO.LOW)
            time.sleep(STEP_DELAY)

            if (i + 1) % 100 == 0:
                print(f"Steps bisher: {i + 1}")

    except KeyboardInterrupt:
        GPIO.cleanup()
        print("❌ Manuell abgebrochen.")

    finally:
        GPIO.output(PIN_EN, GPIO.HIGH)
        GPIO.cleanup()
        print("GPIO cleaned up.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Verwendung:")
        print("  python3 motor_test.py <steps> <richtung>")
        print("Beispiele:")
        print("  python3 motor_test.py 2000 vor")
        print("  python3 motor_test.py 1500 zurueck")
        sys.exit(1)

    steps = int(sys.argv[1])
    direction = sys.argv[2]

    run_steps(steps, direction)
