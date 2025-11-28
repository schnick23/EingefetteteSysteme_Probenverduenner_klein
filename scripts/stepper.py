import RPi.GPIO as GPIO
import time

# ================================
#     KONFIGURATION ANPASSEN
# ================================

# GPIO PINs (BCM numbering)
PIN_STEP = 17
PIN_DIR = 27
PIN_EN = 22   # optional – wenn nicht genutzt: einfach nicht setzen

# Bewegungs-Parameter
MOTOR_STEPS_PER_REV = 200          # Motor = 1.8°
MICROSTEPPING = 16                 # TMC2209 DIP/UART einstellen!
LEADSCREW_MM_PER_REV = 8           # z.B. TR8x8 = 8mm pro Umdrehung

# Geschwindigkeit
STEP_DELAY = 0.0005                # Zeit zwischen Steps (0.5 ms) ≈ 2000 Schritte/s

# ================================
#       BERECHNUNG
# ================================

STEPS_PER_REV = MOTOR_STEPS_PER_REV * MICROSTEPPING
STEPS_PER_MM = STEPS_PER_REV / LEADSCREW_MM_PER_REV
STEPS_PER_CM = STEPS_PER_MM * 10   # da 10 mm

# ================================
#       SETUP
# ================================

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(PIN_STEP, GPIO.OUT)
GPIO.setup(PIN_DIR, GPIO.OUT)
GPIO.setup(PIN_EN, GPIO.OUT)

# Enable aktiv LOW bei TMC2209
GPIO.output(PIN_EN, GPIO.LOW)    # Motor aktiv


# ================================
#       GRUND-FUNKTION
# ================================

def move_cm(cm: float, upwards: bool = True):
    """
    Bewegt den Motor um X Zentimeter.
    cm > 0  = Distanz in cm
    upwards = True  → Richtung A
                False → Richtung B
    """

    # Richtung setzen
    GPIO.output(PIN_DIR, GPIO.HIGH if upwards else GPIO.LOW)

    # Schritte berechnen
    total_steps = int(STEPS_PER_CM * cm)

    print(f"Bewege Motor: {cm} cm → {total_steps} Schritte")

    # Schritt-Ausgabe
    for _ in range(total_steps):
        GPIO.output(PIN_STEP, GPIO.HIGH)
        time.sleep(STEP_DELAY)
        GPIO.output(PIN_STEP, GPIO.LOW)
        time.sleep(STEP_DELAY)


# ================================
#       TEST / HAUPTPROGRAMM
# ================================
if __name__ == "__main__":
    try:
        print("Motor fährt 7 cm aufwärts...")
        move_cm(7, upwards=True)

        time.sleep(1)

        print("Motor fährt 2 cm zurück...")
        move_cm(2, upwards=False)

    except KeyboardInterrupt:
        pass
    finally:
        GPIO.output(PIN_EN, GPIO.HIGH)   # Motor disable
        GPIO.cleanup()
        print("GPIO cleaned up.")
