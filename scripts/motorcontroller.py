#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time


START_DELAY = 0.0015   # sehr langsam (Startmoment)
   # Zielgeschwindigkeit
END_DELAY   = 0.0015   # sanftes Abbremsen

RAMP_STEPS = 300       # Anzahl Schritte für Beschleunigung / Bremsung

class Axis:
    def __init__(
        self,
        name, #Name der Achse HUB, LINEAR, SYRINGE
        pin_step, 
        pin_dir, #Richtung
        pin_en,
        run_delay   = 0.0001,     
        #step_delay=STEP_DELAY,
        dir_high_is_positive=True,
        home_towards_positive=False,
    ):
        GPIO.setmode(GPIO.BCM)
        self.name = name
        self.pin_step = pin_step
        self.pin_dir = pin_dir
        self.pin_en = pin_en
        self.RUN_DELAY   = run_delay
        #self.step_delay = step_delay
        self.dir_high_is_positive = dir_high_is_positive
        self.home_towards_positive = home_towards_positive
        self.current_steps = 0

        GPIO.setup(self.pin_step, GPIO.OUT)
        GPIO.setup(self.pin_dir, GPIO.OUT)
        if self.pin_en is not None:
            GPIO.setup(self.pin_en, GPIO.OUT)
            GPIO.output(self.pin_en, GPIO.LOW)  # Enable aktiv LOW
            
    def _set_dir(self, direction: bool):
        """
        direction = True  -> "positiv"
        direction = False -> "negativ"
        """
        if self.dir_high_is_positive:
            GPIO.output(self.pin_dir, GPIO.HIGH if direction else GPIO.LOW)
        else:
            GPIO.output(self.pin_dir, GPIO.LOW if direction else GPIO.HIGH)
    


    def _lerp(self, start: float, end: float, t: float) -> float:
        return start + (end - start) * max(0.0, min(1.0, t))

    def _do_step(self, steps: int, direction: bool):
        if steps <= 0:
            return

        self._set_dir(direction)

        # Nutze die globalen Konstanten
        ramp_steps = min(steps // 2, RAMP_STEPS)

        for i in range(steps):

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

            # Endschalter hier prüfen
    
    def do_step_linear(self, steps: int, direction: bool):
     
        if steps <= 0:
            return
        self._set_dir(direction)
        for _ in range(steps):
            GPIO.output(self.pin_step, GPIO.HIGH)
            time.sleep(self.RUN_DELAY)
            GPIO.output(self.pin_step, GPIO.LOW)
            time.sleep(self.RUN_DELAY)
            if direction:
                self.current_steps += 1
            else:
                self.current_steps -= 1



    def _home(self):
        # Fahre zurück auf 0 basierend auf dem aktuellen Zählerstand
        steps_to_move = abs(self.current_steps)
        
        if steps_to_move == 0:
            return

        # Wenn wir bei +1000 sind, müssen wir in negative Richtung (False) fahren
        # Wenn wir bei -1000 sind, müssen wir in positive Richtung (True) fahren
        direction = False if self.current_steps > 0 else True
        
        self._do_step(steps_to_move, direction)
