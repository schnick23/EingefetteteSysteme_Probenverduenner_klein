#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time


STEP_DELAY = 0.000005             # 0.5 ms → ca. 2000 Schritte/s

class Axis:
    def __init__(
        self,
        name, #Name der Achse HUB, LINEAR, SYRINGE
        pin_step, 
        pin_dir, #Richtung
        pin_en,     
        step_delay=STEP_DELAY,
        dir_high_is_positive=True,
        home_towards_positive=False,
    ):
        GPIO.setmode(GPIO.BCM)
        self.name = name
        self.pin_step = pin_step
        self.pin_dir = pin_dir
        self.pin_en = pin_en
        self.step_delay = step_delay
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
    
    def _do_step(self, steps: int, direction: bool):
        self._set_dir(direction)
        for _ in range(steps):
            GPIO.output(self.pin_step, GPIO.HIGH)
            time.sleep(self.step_delay)
            GPIO.output(self.pin_step, GPIO.LOW)
            time.sleep(self.step_delay)
            if direction:
                self.current_steps += 1
            else:
                self.current_steps -= 1
            # Endschalter prüfen

    def _home(self):
        while self.current_steps != 0:
            if self.home_towards_positive:
                self._do_step(self.current_steps, True)
            else:
                self._do_step((self.current_steps*-1), False)
