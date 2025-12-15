#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

from .motorcontroller import Axis


class SyringeHead:
    """
    Kapselt eine Axis und bietet funktionen in ml statt in Schritten.
    - ml → Schritte wird über steps_per_ml kalibriert.
    - Es wird ein aktuelles Volumen (in ml) mitgeführt.
    """

    def __init__(
        self,
        axis,
        steps_per_ml: int,
        max_volume_ml: float,
        draw_towards_positive: bool = True,
        start_volume_ml: float = 0.0,
        endstop_pin_links: int = None,
        endstop_pin_rechts: int = None
    ):
        """
        axis              : Instanz der Axis-Klasse (z.B. name="SYRINGE")
        steps_per_ml      : Kalibrierwert: wie viele Steps pro ml?
        max_volume_ml     : Maximales Volumen der Spritze
        draw_towards_pos  : True, wenn "aufsaugen" (ziehen) in positiver Richtung geschehen soll
        start_volume_ml   : Startfüllung in ml (Default: 0 = leer)
        """
        GPIO.setmode(GPIO.BCM)
        self.AXIS = axis
        self.steps_per_ml = steps_per_ml
        self.max_volume_ml = max_volume_ml
        self.draw_towards_positive = draw_towards_positive
        self.END_STOP_PIN_LINKS = endstop_pin_links
        if self.END_STOP_PIN_LINKS is not None:
            GPIO.setup(self.END_STOP_PIN_LINKS, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.END_STOP_PIN_RECHTS = endstop_pin_rechts
        if self.END_STOP_PIN_RECHTS is not None:
            GPIO.setup(self.END_STOP_PIN_RECHTS, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Interner Zustand
        self.current_volume_ml = float(start_volume_ml)

        # Optional: Axis-Position konsistent zum Volumen setzen
        # Referenz: Volumen 0 ml → aktuelle Steps als 0 ansehen
        self.AXIS.current_steps = 0

    # ==============================
    #   HILFSFUNKTIONEN (INTERN)
    # ==============================

    def _ml_to_steps(self, ml: float) -> int:
        return int(round(ml * self.steps_per_ml))

    def _move_relative_ml(self, delta_ml: float):
        """
        Bewegt die Spritze relativ um delta_ml:
        +delta_ml => mehr Volumen (ziehen)
        -delta_ml => weniger Volumen (ausgeben)

        Achtung: delta_ml kann bei Clamping kleiner werden.
        """
        if delta_ml == 0:
            return

        # Zielvolumen berechnen und clampen
        target_volume = self._clamp_volume(self.current_volume_ml + delta_ml)
        effective_delta_ml = target_volume - self.current_volume_ml

        if effective_delta_ml == 0:
            # Keine reale Änderung (z.B. weil max oder min erreicht wurde)
            return

        steps = abs(self._ml_to_steps(effective_delta_ml))

        # Richtung bestimmen:
        # - Wenn wir mehr Volumen haben wollen (ziehen): draw_towards_positive
        # - Wenn wir weniger Volumen haben wollen (ausgeben): die Gegenrichtung
        if effective_delta_ml > 0:
            direction = self.draw_towards_positive
        else:
            direction = not self.draw_towards_positive

        # Achse bewegen
        self.AXIS._do_step(steps, direction)

        # Zustand aktualisieren
        self.current_volume_ml = target_volume

    # ==============================
    #   ÖFFENTLICHE METHODEN
    # ==============================

    def aspirate(self, volume_ml: float):
        """
        Zieht volume_ml in die Spritze (ml werden hinzugefügt).
        Begrenzung: max_volume_ml.
        """
        print(f"[SYRINGE] Aspirate: +{volume_ml} ml")
        self._move_relative_ml(volume_ml)
        print(f"[SYRINGE] Aktuelles Volumen: {self.current_volume_ml:.3f} ml")

    def dispense(self, volume_ml: float):
        """
        Gibt volume_ml aus der Spritze ab (ml werden reduziert).
        Begrenzung: minimal 0 ml.
        """
        print(f"[SYRINGE] Dispense: -{volume_ml} ml")
        self._move_relative_ml(-volume_ml)
        print(f"[SYRINGE] Aktuelles Volumen: {self.current_volume_ml:.3f} ml")

    def go_to_volume(self, target_volume_ml: float):
        """
        Direkt auf ein absolutes Volumen fahren, z. B. 0 ml = leer oder 5 ml.
        """
        target_volume_ml = self._clamp_volume(target_volume_ml)
        delta_ml = target_volume_ml - self.current_volume_ml
        print(f"[SYRINGE] Go to volume: {target_volume_ml} ml (Δ={delta_ml:+.3f} ml)")
        self._move_relative_ml(delta_ml)
        print(f"[SYRINGE] Aktuelles Volumen: {self.current_volume_ml:.3f} ml")

    def is_empty(self) -> bool:
        return self.current_volume_ml <= 0.0001

    def is_full(self) -> bool:
        return self.current_volume_ml >= (self.max_volume_ml - 0.0001)
    
    def home(self):
        print(f"[{self.AXIS.name}] Homing...")
        
        # In Richtung Homing fahren, bis Endstopp erreicht
        direction = self.draw_towards_positive
        while GPIO.input(self.END_STOP_PIN_RECHTS) == GPIO.HIGH or GPIO.input(self.END_STOP_PIN_LINKS) == GPIO.HIGH:
            self.AXIS._do_step(10, direction)

        # Position auf 0 setzen
        self.AXIS.current_steps = 0
        self.current_volume_ml = 0.0
        print(f"[{self.AXIS.name}] Homing abgeschlossen. Position und Volumen auf 0 gesetzt.")
