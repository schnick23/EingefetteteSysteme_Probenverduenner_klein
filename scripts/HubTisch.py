#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

from motorcontroller import Axis
class Hubtisch:
    # ==============================
    #   KONFIGURATION HUB-ACHSE
    # ==============================

    # Positionen in "Schritten"
    HUB_BOTTOM_STEPS = 0          # unten = 0
    HUB_CLEANING_STEPS = 4000
    HUB_COVER_STEPS = 5000
    HUB_TOP_STEPS    = 8000       # oben = DIESEN WERT KALIBRIEREN!

    # Wenn True: DIR-Pin HIGH = nach oben; sonst umgekehrt
    DIR_HIGH_IS_POSITIVE = True

    def __init__(
        self,
        name, #Name der Achse HUB, LINEAR, SYRINGE
        pin_step, 
        pin_dir, #Richtung
        pin_en
    ):
        self.name = name
        # GPIO-Nummern (BCM)
        self.HUB_PIN_STEP = pin_step
        self.HUB_PIN_DIR = pin_dir
        self.HUB_PIN_EN = pin_en # optional, kann auch None sein, falls nicht verdrahtet

    # ==============================
    #   HILFSFUNKTIONEN
    # ==============================

    def move_to_position(self, axis: Axis, target_steps: int):
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


    def move_hub_to_bottom(self, axis: Axis):
        print("\n=== HUBTISCH: FAHRE NACH UNTEN ===")
        self.move_to_position(axis, self.HUB_BOTTOM_STEPS)


    def move_hub_to_top(self, axis: Axis):
        print("\n=== HUBTISCH: FAHRE NACH OBEN ===")
        self.move_to_position(axis, self.HUB_TOP_STEPS)


    def setup_gpio():
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)


    def cleanup_gpio(hub_axis: Axis | None = None):
        # ggf. Achse deaktivieren (Enable HIGH bei aktiv LOW)
        if hub_axis is not None and hub_axis.pin_en is not None:
            GPIO.output(hub_axis.pin_en, GPIO.HIGH)
        GPIO.cleanup()