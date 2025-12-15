#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
from simulation_mode import is_simulation, sim_print

#Anfahrrampe für Stepper-Motoren
START_DELAY = 0.0015   # sehr langsam (Startmoment)
END_DELAY   = 0.0015   # sanftes Abbremsen
RAMP_STEPS = 300       # Anzahl Schritte für Beschleunigung / Bremsung

class Axis:
    def __init__(
        self,
        name, #Name der Achse HUB, LINEAR, SYRINGE
        pin_step, 
        pin_dir, #Richtung
        pin_en,
        run_delay = 0.0001, #delay zwischen den Schritten (Default: 0.0001)     
        dir_high_is_positive=True,
        home_towards_positive=True,
        endstop_pins: list[int] = None
    
    ):
        GPIO.setmode(GPIO.BCM)
        self.name = name
        self.pin_step = pin_step
        self.pin_dir = pin_dir
        self.pin_en = pin_en
        self.RUN_DELAY   = run_delay
        self.dir_high_is_positive = dir_high_is_positive
        self.home_towards_positive = home_towards_positive
        self.current_steps = 0
        self.END_STOP_PIN = endstop_pins

        if not is_simulation():
            GPIO.setup(self.pin_step, GPIO.OUT)
            GPIO.setup(self.pin_dir, GPIO.OUT)
            if self.pin_en is not None:
                GPIO.setup(self.pin_en, GPIO.OUT)
                GPIO.output(self.pin_en, GPIO.LOW)  # Enable aktiv LOW
        else:
            sim_print(f"Axis '{self.name}' initialisiert (Simulation)")
            
    def _set_dir(self, direction: bool):
        """
        direction = True  -> "positiv"
        direction = False -> "negativ"
        """
        if not is_simulation():
            if self.dir_high_is_positive:
                GPIO.output(self.pin_dir, GPIO.HIGH if direction else GPIO.LOW)
            else:
                GPIO.output(self.pin_dir, GPIO.LOW if direction else GPIO.HIGH)
    


    def _lerp(self, start: float, end: float, t: float) -> float:
        return start + (end - start) * max(0.0, min(1.0, t))

    def _do_step(self, steps: int, direction: bool):
        if steps <= 0:
            return

        if is_simulation():
            if direction:
                self.current_steps += steps
            else:
                self.current_steps -= steps
            # Reduziertes Logging: keine Schritt-/Positionszahlen
            sim_print(f"[{self.name}] Bewegung (sim), Richtung: {'vorwärts' if direction else 'rückwärts'}")
            return

        if self.home_towards_positive:
            direction = direction
        else:
            direction = not direction

        # Echtbetrieb: Start-Log
        # Reduziertes Logging: keine Schritt-/Positionszahlen
        print(f"[{self.name}] Starte Bewegung, Richtung: {'vorwärts' if direction else 'rückwärts'}")
        self._set_dir(direction)

        # Nutze die globalen Konstanten
        ramp_steps = min(steps // 2, RAMP_STEPS)
        for i in range(steps):
            endstop = False
            # Endstopp nur prüfen, wenn Pins konfiguriert sind
            if self.END_STOP_PIN is not None:
                for pin in self.END_STOP_PIN:
                    if GPIO.input(pin) == GPIO.LOW:
                        endstop = True
                        break
            if self.END_STOP_PIN is not None and endstop == True and direction == (not self.home_towards_positive):
                break

            # --- Rampe berechnen ---
            if i < ramp_steps:
                # Beschleunigung
                delay = self._lerp(
                    start=START_DELAY,
                    end=self.RUN_DELAY,
                    t=i / ramp_steps
                )
            elif i > steps - ramp_steps:
                # Bremsen
                delay = self._lerp(
                    start=self.RUN_DELAY,
                    end=END_DELAY,
                    t=(i - (steps - ramp_steps)) / ramp_steps
                )
            else:
                # konstante Geschwindigkeit
                delay = self.RUN_DELAY

            GPIO.output(self.pin_step, GPIO.HIGH)
            time.sleep(delay)
            GPIO.output(self.pin_step, GPIO.LOW)
            time.sleep(delay)

            if direction:
                self.current_steps += 1
            else:
                self.current_steps -= 1
        # Echtbetrieb: End-Log
        # Reduziertes Logging: keine Schritt-/Positionszahlen
        print(f"[{self.name}] Bewegung abgeschlossen")
            
    
    def do_step_linear(self, steps: int, direction: bool):
        if steps <= 0:
            return
            
        if is_simulation():
            if direction:
                self.current_steps += steps
            else:
                self.current_steps -= steps
            # Reduziertes Logging: keine Schritt-/Positionszahlen
            sim_print(f"[{self.name}] Linearbewegung (sim), Richtung: {'vorwärts' if direction else 'rückwärts'}")
            return
            
        
        if self.home_towards_positive:
            direction = direction
        else:
            direction = not direction
        # Echtbetrieb: Start-Log
        # Reduziertes Logging: keine Schritt-/Positionszahlen
        print(f"[{self.name}] Starte lineare Bewegung, Richtung: {'vorwärts' if direction else 'rückwärts'}")
        self._set_dir(direction)
        for _ in range(steps):
            endstop = False
            # Endstopp nur prüfen, wenn Pins konfiguriert sind
            if self.END_STOP_PIN is not None:
                for pin in self.END_STOP_PIN:
                    if GPIO.input(pin) == GPIO.LOW:
                        endstop = True
                        break
            if self.END_STOP_PIN is not None and endstop == True and direction == False:
                break
            GPIO.output(self.pin_step, GPIO.HIGH)
            time.sleep(self.RUN_DELAY)
            GPIO.output(self.pin_step, GPIO.LOW)
            time.sleep(self.RUN_DELAY)
            if direction:
                self.current_steps += 1
            else:
                self.current_steps -= 1
        # Echtbetrieb: End-Log
        # Reduziertes Logging: keine Schritt-/Positionszahlen
        print(f"[{self.name}] Lineare Bewegung abgeschlossen")