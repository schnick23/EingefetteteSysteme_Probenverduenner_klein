#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

from motorcontroller import Axis

class LinearFuehrung:

    # ==============================
    #   KONFIGURATION LINEAR-ACHSE
    # ==============================

    def __init__(self, axis, endstop_pin_vorne: int = None, endstop_pin_hinten: int = None):
        # GPIO-Nummern (BCM)

        self.AXIS = axis
        self.END_STOP_PIN_VORNE = endstop_pin_vorne
        self.END_STOP_PIN_HINTEN = endstop_pin_hinten
        if self.END_STOP_PIN_VORNE is not None:
            GPIO.setup(self.END_STOP_PIN_VORNE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        if self.END_STOP_PIN_HINTEN is not None:
            GPIO.setup(self.END_STOP_PIN_HINTEN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        
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
    
    def home_linear(self):
        if self.END_STOP_PIN_HINTEN is None:
            print(f"[{self.AXIS.name}] Kein hinterer Endschalter definiert. Homing nicht möglich.")
            return

        print(f"[{self.AXIS.name}] Starte Homing der Linearachse...")
        direction = True 
        print(f"[{self.AXIS.name}] Fahre in Richtung "
              f"{'positiv' if direction else 'negativ'} zum Homing...")

        while GPIO.input(self.END_STOP_PIN_VORNE) == GPIO.HIGH and GPIO.input(self.END_STOP_PIN_HINTEN) == GPIO.HIGH:
            self.AXIS._do_step(1, direction)

        print(f"[{self.AXIS.name}] Hinterer Endschalter ausgelöst!")
        self.AXIS.current_steps = 0
        print(f"[{self.AXIS.name}] Homing abgeschlossen. Position auf 0 gesetzt.")
