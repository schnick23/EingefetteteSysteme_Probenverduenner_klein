#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

from motorcontroller import Axis

class LinearFuehrung:

    # ==============================
    #   KONFIGURATION LINEAR-ACHSE
    # ==============================

    def __init__(self, axis):
        # GPIO-Nummern (BCM)

        self,AXIS = axis
        
    # Positionen in Schritten (absolut, relativ zur 1. Position)
    # WERTE NOCH KALIBRIEREN
    # POSITIONEN NOCH ZUORDNEN
    LINEAR_POSITIONS = {
        1: 0,        # Pos 1 = Anfangsposition
        2: 6000,     # Pos 2 = 1. Reihe
        3: 8000,     # Pos 3 = 2. Reihe
        4: 10000,     # Pos 4 = 3. Reihe
        5: 12000,     # Pos 5 = 4. Reihe
        6: 2000,    # Pos 6 = Reinigungsbehälter
        7: 4000,    # Pos 7 = Abfallbehälter
        8: 14000,    # Pos 8 = Abdeckungsposition
    }

    # DIR_HIGH_IS_POSITIVE = True   # ggf. umdrehen, wenn Richtung „falsch herum“


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


    def move_linear_to_index(self, index: int):
        """
        Fahre die Linearachse auf die Position mit Index 1..8.
        """
        if index not in self.LINEAR_POSITIONS:
            print(f"[{self.AXIS.name}] Ungültiger Positionsindex: {index}")
            return

        target_steps = self.LINEAR_POSITIONS[index]
        print(f"\n=== LINEAR: FAHRE ZU POSITION {index} (Ziel: {target_steps} Schritte) ===")
        self.move_to_position(self.AXIS, target_steps)


    def setup_gpio():
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)


    def cleanup_gpio(self):
        if self.AXIS is not None and self.AXIS.pin_en is not None:
            GPIO.output(self.AXIS.pin_en, GPIO.HIGH)  # Motor deaktivieren (Enable HIGH bei aktiv LOW)
        GPIO.cleanup()
