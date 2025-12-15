#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

from .motorcontroller import Axis

class LinearFuehrung:

    # ==============================
    #   KONFIGURATION LINEAR-ACHSE
    # ==============================

    def __init__(self, axis, endstop_pin_vorne: int = None, endstop_pin_hinten: int = None):
        # GPIO-Nummern (BCM)
        GPIO.setmode(GPIO.BCM)
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
        1: 95000,        # Pos 1 = Abdeckungsposition
        2: 73300,     # Pos 2 = Reihe 0 --> Stammlösung
        4: 61800,     # Pos 4 = 1. Verdünnungsreihe
        3: 50300,     # Pos 3 = 2. Verdünnungsreihe
        5: 38300,     # Pos 5 = 3. Verdünnungsreihe
        6: 30300,    # Pos 6 = Reinigungsbehälter
        7: 22300,    # Pos 7 = Abfallbehälter
        8: 0,    # Pos 8 = Home Position (Endstopp hintend)
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
    
    def home(self):
        if self.END_STOP_PIN_HINTEN is None:
            print(f"[{self.AXIS.name}] Kein hinterer Endschalter definiert. Homing nicht möglich.")
            return

        print(f"[{self.AXIS.name}] Starte Homing der Linearachse...")
        direction = False 
        print("Fahre nach hinten zum Homing...")

        while GPIO.input(self.END_STOP_PIN_HINTEN) == GPIO.HIGH:
            self.AXIS.do_step_linear(10, direction)

        print(f"[{self.AXIS.name}] Hinterer Endschalter ausgelöst!")
        self.AXIS.current_steps = self.LINEAR_POSITIONS[8]
        print(f"[{self.AXIS.name}] Homing abgeschlossen. Position auf 8 gesetzt.")
    
    def home_vorne(self):
        if self.END_STOP_PIN_VORNE is None:
            print(f"[{self.AXIS.name}] Kein vorderer Endschalter definiert. Homing nicht möglich.")
            return

        print(f"[{self.AXIS.name}] Starte Homing der Linearachse...")
        direction = True 
        print("Fahre nach vorne zum Homing...")

        while GPIO.input(self.END_STOP_PIN_VORNE) == GPIO.HIGH:
            self.AXIS.do_step_linear(10, direction)

        print(f"[{self.AXIS.name}] Vorderer Endschalter ausgelöst!")
        self.AXIS.current_steps = self.LINEAR_POSITIONS[1]
        print(f"[{self.AXIS.name}] Homing abgeschlossen. Position auf 1 gesetzt.")