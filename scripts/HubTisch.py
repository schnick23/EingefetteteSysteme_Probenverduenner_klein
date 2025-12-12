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
        AXIS
    ):
        self.AXIS = AXIS

    # ==============================
    #   HILFSFUNKTIONEN
    # ==============================

    def move_to_position(self, target_steps: int):
        """
        Fahre die Achse auf eine absolute Zielposition (in Schritten).
        Annahme: axis.current_steps ist immer die aktuell bekannte Position.
        """
        delta = target_steps - self.AXIS.current_steps

        if delta == 0:
            print(f"[{self.AXIS.name}] Bereits an der Zielposition ({target_steps} Schritte).")
            return

        direction = delta > 0
        steps = abs(delta)

        print(f"[{self.AXIS.name}] Bewege {steps} Schritte in Richtung "
            f"{'positiv' if direction else 'negativ'}...")
        self.AXIS._do_step(steps, direction)
        print(f"[{self.AXIS.name}] Neue Position: {self.AXIS.current_steps} Schritte")


    def move_hub_to_bottom(self):
        print("\n=== HUBTISCH: FAHRE NACH UNTEN ===")
        self.move_to_position(self.AXIS, self.HUB_BOTTOM_STEPS)


    def move_hub_to_top(self):
        print("\n=== HUBTISCH: FAHRE NACH OBEN ===")
        self.move_to_position(self.AXIS, self.HUB_TOP_STEPS)
    
    def move_hub_to_cleaning(self):
        print("\n=== HUBTISCH: FAHRE ZUR REINIGUNGSPOSITION ===")
        self.move_to_position(self.AXIS, self.HUB_CLEANING_STEPS)
    
    def move_hub_to_cover(self):
        print("\n=== HUBTISCH: FAHRE ZUR ABDECKUNGSPOSITION ===")
        self.move_to_position(self.AXIS, self.HUB_COVER_STEPS)

    def setup_gpio():
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)


    def cleanup_gpio(self):
        # ggf. Achse deaktivieren (Enable HIGH bei aktiv LOW)
        if self.AXIS is not None and self.AXIS.pin_en is not None:
            GPIO.output(self.AXIS.pin_en, GPIO.HIGH)
        GPIO.cleanup()