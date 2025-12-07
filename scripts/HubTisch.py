#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

from motorcontroller import Axis

# ==============================
#   KONFIGURATION HUB-ACHSE
# ==============================

# GPIO-Nummern (BCM)
HUB_PIN_STEP = 23
HUB_PIN_DIR  = 24
HUB_PIN_EN   = 25  # optional, kann auch None sein, falls nicht verdrahtet

# Positionen in "Schritten"
HUB_BOTTOM_STEPS = 0          # unten = 0
HUB_CLEANING_STEPS = 4000
HUB_COVER_STEPS = 5000
HUB_TOP_STEPS    = 8000       # oben = DIESEN WERT KALIBRIEREN!

# Wenn True: DIR-Pin HIGH = nach oben; sonst umgekehrt
DIR_HIGH_IS_POSITIVE = True

# ==============================
#   HILFSFUNKTIONEN
# ==============================

def move_to_position(axis: Axis, target_steps: int):
    """
    Fahre die Achse auf eine absolute Zielposition (in Schritten).
    Annahme: axis.current_steps ist immer die aktuell bekannte Position.
    """
    delta = target_steps - axis.current_steps

    if delta == 0:
        print(f"[{axis.name}] Bereits an der Zielposition ({target_steps} Schritte).")
        return

    direction = delta > 0
    steps = abs(delta)

    print(f"[{axis.name}] Bewege {steps} Schritte in Richtung "
          f"{'positiv' if direction else 'negativ'}...")
    axis._do_step(steps, direction)
    print(f"[{axis.name}] Neue Position: {axis.current_steps} Schritte")


def move_hub_to_bottom(axis: Axis):
    print("\n=== HUBTISCH: FAHRE NACH UNTEN ===")
    move_to_position(axis, HUB_BOTTOM_STEPS)


def move_hub_to_top(axis: Axis):
    print("\n=== HUBTISCH: FAHRE NACH OBEN ===")
    move_to_position(axis, HUB_TOP_STEPS)


def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)


def cleanup_gpio(hub_axis: Axis | None = None):
    # ggf. Achse deaktivieren (Enable HIGH bei aktiv LOW)
    if hub_axis is not None and hub_axis.pin_en is not None:
        GPIO.output(hub_axis.pin_en, GPIO.HIGH)
    GPIO.cleanup()


# ==============================
#   HAUPTPROGRAMM
# ==============================

def main():
    setup_gpio()

    # Annahme: Beim Start steht der Hubtisch ganz unten.
    # Wenn das stimmt: current_steps = 0
    hub_axis = Axis(
        name="HUB",
        pin_step=HUB_PIN_STEP,
        pin_dir=HUB_PIN_DIR,
        pin_en=HUB_PIN_EN,
        dir_high_is_positive=DIR_HIGH_IS_POSITIVE,
        home_towards_positive=False,   # aktuell unbenutzt
    )
    hub_axis.current_steps = HUB_BOTTOM_STEPS

    try:
        while True:
            print("\n======================")
            print("  HUBTISCH-STEUERUNG  ")
            print("======================")
            print("[1] Nach OBEN fahren")
            print("[2] Nach UNTEN fahren")
            print("[q] Beenden")
            choice = input("Auswahl: ").strip().lower()

            if choice == "1":
                move_hub_to_top(hub_axis)
            elif choice == "2":
                move_hub_to_bottom(hub_axis)
            elif choice == "q":
                print("Beende Programm...")
                break
            else:
                print("Ungültige Eingabe.")

    except KeyboardInterrupt:
        print("\nAbgebrochen mit STRG+C.")

    finally:
        cleanup_gpio(hub_axis)


if __name__ == "__main__":
    main()
