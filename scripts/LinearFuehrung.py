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
# WERTE NOCH KALIBRIEREN
# POSITIONEN NOCH ZUORDNEN
LINEAR_POSITIONS = {
    1: 0,        # Pos 1 = Anfangsposition
    2: 2000,     # Pos 2 = 1. Reihe
    3: 4000,     # Pos 3 = 2. Reihe
    4: 6000,     # Pos 4 = 3. Reihe
    5: 8000,     # Pos 5 = 4. Reihe
    6: 10000,    # Pos 6 = Reinigungsbehälter
    7: 12000,    # Pos 7 = Abfallbehälter
    8: 14000,    # Pos 8 = Abdeckungsposition
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

