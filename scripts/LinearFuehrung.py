#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

from motorcontroller import Axis

# ==============================
#   KONFIGURATION LINEAR-ACHSE
# ==============================

# GPIO-Nummern (BCM)
LIN_PIN_STEP = 16
LIN_PIN_DIR  = 20
LIN_PIN_EN   = 21   

# Positionen in Schritten (absolut, relativ zur 1. Position)
# Diese Werte MUSST du selbst kalibrieren!
# Beispiel: alle 2000 Schritte eine Position weiter.
LINEAR_POSITIONS = {
    1: 0,        # Pos 1
    2: 2000,     # Pos 2
    3: 4000,     # Pos 3
    4: 6000,     # Pos 4
    5: 8000,     # Pos 5
    6: 10000,    # Pos 6
    7: 12000,    # Pos 7
    8: 14000,    # Pos 8
}

DIR_HIGH_IS_POSITIVE = True   # ggf. umdrehen, wenn Richtung „falsch herum“


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


def move_linear_to_index(axis: Axis, index: int):
    """
    Fahre die Linearachse auf die Position mit Index 1..8.
    """
    if index not in LINEAR_POSITIONS:
        print(f"[{axis.name}] Ungültiger Positionsindex: {index}")
        return

    target_steps = LINEAR_POSITIONS[index]
    print(f"\n=== LINEAR: FAHRE ZU POSITION {index} (Ziel: {target_steps} Schritte) ===")
    move_to_position(axis, target_steps)


def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)


def cleanup_gpio(axis: Axis | None = None):
    if axis is not None and axis.pin_en is not None:
        GPIO.output(axis.pin_en, GPIO.HIGH)  # Motor deaktivieren (Enable HIGH bei aktiv LOW)
    GPIO.cleanup()


# ==============================
#   HAUPTPROGRAMM
# ==============================

def main():
    setup_gpio()

    # Annahme: Beim Start steht die Linearführung an Position 1
    # → absolute Schritte = LINEAR_POSITIONS[1]
    linear_axis = Axis(
        name="LINEAR",
        pin_step=LIN_PIN_STEP,
        pin_dir=LIN_PIN_DIR,
        pin_en=LIN_PIN_EN,
        dir_high_is_positive=DIR_HIGH_IS_POSITIVE,
        home_towards_positive=False,
    )
    linear_axis.current_steps = LINEAR_POSITIONS[1]

    try:
        while True:
            print("\n==========================")
            print("  LINEARFÜHRUNG-STEUERUNG ")
            print("==========================")
            print("Wähle Zielposition (1–8) oder 'q' zum Beenden.")
            for i in range(1, 9):
                print(f"[{i}] Position {i} (Steps: {LINEAR_POSITIONS[i]})")
            print("[q] Beenden")

            choice = input("Auswahl: ").strip().lower()

            if choice == "q":
                print("Beende Programm...")
                break

            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= 8:
                    move_linear_to_index(linear_axis, idx)
                else:
                    print("Ungültige Position. Bitte 1–8 wählen.")
            else:
                print("Ungültige Eingabe.")

    except KeyboardInterrupt:
        print("\nAbgebrochen mit STRG+C.")

    finally:
        cleanup_gpio(linear_axis)


if __name__ == "__main__":
    main()
