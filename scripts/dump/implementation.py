#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

# ============================================
#   PIN-KONFIGURATION (BCM)
# ============================================
# Achsen (TMC2209 / TB6600)
PIN_SYRINGE_STEP = 17      # TMC2209 #1 STEP
PIN_SYRINGE_DIR  = 27      # TMC2209 #1 DIR
PIN_SYRINGE_EN   = 22      # TMC2209 #1 EN (aktiv LOW)

PIN_HUB_STEP = 23      # TMC2209 #2 STEP (noch nicht genutzt)
PIN_HUB_DIR  = 24
PIN_HUB_EN   = 25

PIN_LINEAR_STEP = 16       # TB6600 STEP
PIN_LINEAR_DIR  = 20      # TB6600 DIR
PIN_LINEAR_EN   = 21      # TB6600 EN (aktiv LOW)

# Endstops (Schalter gegen GND, interner Pull-Up aktiv)
PIN_ENDSTOP_SYRINGE = 5
PIN_ENDSTOP_HUB = 6
PIN_ENDSTOP_LINEAR = 13

# Relais / Pumpen (5 Kanäle)
PIN_RELAY_1 = 12
PIN_RELAY_2 = 1    # Achtung: BCM 1 ist I²C SDA – nur verwenden, wenn wirklich frei!
PIN_RELAY_3 = 7
PIN_RELAY_4 = 8
PIN_RELAY_5 = 18

# ============================================
#   ACHSEN-KONSTANTEN (ANPASSEN!)
# ============================================

STEP_DELAY = 0.0005             # 0.5 ms → ca. 2000 Schritte/s

# LINEAER STEPS
STEPS_PER_REV_LINEAR = 200 # 1.8° Motor
STEPS_PER_MM_LINEAR  = 40 # Linearachse - 5mm/Umdrehung
#

# Positionstabellen in MILLIMETER (NOCHMAL ÄNDERN!)
# z. B. 8 Spalten à 10 mm Abstand auf X
LINEAR_POSITIONS_MM = [
    0.0,   # Index 0
    10.0,  # Index 1
    20.0,  # Index 2
    30.0,  # Index 3
    40.0,  # Index 4
    50.0,  # Index 5
    60.0,  # Index 6
    70.0,  # Index 7
]

# z. B. 4 Höhen auf Z
HUB_POSITIONS_MM = [
    0.0,   # Index 0
    20.0,  # Index 1
    40.0,  # Index 2
    60.0,  # Index 3
]

# ============================================
#   RELAIS-KONFIGURATION (Pumpen)
# ============================================

RELAY_ACTIVE_STATE   = GPIO.HIGH
RELAY_INACTIVE_STATE = GPIO.LOW

PUMP_PINS = {
    1: PIN_RELAY_1,
    2: PIN_RELAY_2,
    3: PIN_RELAY_3,
    4: PIN_RELAY_4,
    5: PIN_RELAY_5,
}

# ============================================
#   KLASSEN
# ============================================

class Axis:
    def __init__(
        self,
        name, #Name der Achse HUB, LINEAR, SYRINGE
        pin_step, 
        pin_dir, #Richtung
        pin_en, 
        pin_endstop, #Endschalter
        steps_per_mm,
        step_delay=STEP_DELAY,
        dir_high_is_positive=True,
        home_towards_positive=False,
    ):
        self.name = name
        self.pin_step = pin_step
        self.pin_dir = pin_dir
        self.pin_en = pin_en
        self.pin_endstop = pin_endstop
        self.steps_per_mm = steps_per_mm
        self.step_delay = step_delay
        self.dir_high_is_positive = dir_high_is_positive
        self.home_towards_positive = home_towards_positive

        self.current_steps = 0

        GPIO.setup(self.pin_step, GPIO.OUT)
        GPIO.setup(self.pin_dir, GPIO.OUT)
        if self.pin_en is not None:
            GPIO.setup(self.pin_en, GPIO.OUT)
            GPIO.output(self.pin_en, GPIO.LOW)  # Enable aktiv LOW

        if self.pin_endstop is not None:
            GPIO.setup(self.pin_endstop, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def _set_dir(self, positive: bool):
        if self.dir_high_is_positive:
            GPIO.output(self.pin_dir, GPIO.HIGH if positive else GPIO.LOW)
        else:
            GPIO.output(self.pin_dir, GPIO.LOW if positive else GPIO.HIGH)

    def _is_endstop_triggered(self) -> bool:
        if self.pin_endstop is None:
            return False
        # Pull-Up: LOW = ausgelöst
        return GPIO.input(self.pin_endstop) == GPIO.LOW

    def _do_step(self, steps: int, positive: bool):
        self._set_dir(positive)
        for _ in range(steps):
            GPIO.output(self.pin_step, GPIO.HIGH)
            time.sleep(self.step_delay)
            GPIO.output(self.pin_step, GPIO.LOW)
            time.sleep(self.step_delay)
        self.current_steps += (steps if positive else -steps)

    def move_mm_relative(self, delta_mm: float):
        steps = int(abs(delta_mm) * self.steps_per_mm)
        if steps == 0:
            return
        positive = delta_mm > 0
        print(f"[{self.name}] move rel {delta_mm} mm → {steps} steps")
        self._do_step(steps, positive)

    def move_to_mm(self, target_mm: float):
        target_steps = int(target_mm * self.steps_per_mm)
        delta_steps = target_steps - self.current_steps
        if delta_steps == 0:
            print(f"[{self.name}] bereits an {target_mm} mm")
            return
        positive = delta_steps > 0
        steps = abs(delta_steps)
        print(f"[{self.name}] move abs {target_mm} mm → Δ {delta_steps} steps")
        self._do_step(steps, positive)

    def home(self, max_mm: float = 200.0):
        if self.pin_endstop is None:
            print(f"[{self.name}] kein Endstop → kein Homing")
            return

        print(f"[{self.name}] Homing startet...")
        positive = self.home_towards_positive
        max_steps = int(max_mm * self.steps_per_mm)
        steps_done = 0

        while not self._is_endstop_triggered() and steps_done < max_steps:
            self._do_step(1, positive)
            steps_done += 1

        if self._is_endstop_triggered():
            print(f"[{self.name}] Endstop nach {steps_done} Steps erreicht")
        else:
            print(f"[{self.name}] WARNUNG: max_mm erreicht, Endstop nicht gefunden")

        # Nullpunkt setzen
        self.current_steps = 0


class PumpController:
    def __init__(self, pump_pins: dict[int, int]):
        self.pump_pins = pump_pins
        for pin in self.pump_pins.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, RELAY_INACTIVE_STATE)

    def pump_on(self, pump_id: int):
        pin = self.pump_pins[pump_id]
        GPIO.output(pin, RELAY_ACTIVE_STATE)
        print(f"[PUMP] {pump_id} EIN (Pin {pin})")

    def pump_off(self, pump_id: int):
        pin = self.pump_pins[pump_id]
        GPIO.output(pin, RELAY_INACTIVE_STATE)
        print(f"[PUMP] {pump_id} AUS (Pin {pin})")

    def pump_for_seconds(self, pump_id: int, seconds: float):
        self.pump_on(pump_id)
        time.sleep(seconds)
        self.pump_off(pump_id)

    def pump_for_ml(self, pump_id: int, volume_ml: float):
        seconds = volume_ml * SECONDS_PER_ML
        print(f"[PUMP] {pump_id} → {volume_ml} ml (~{seconds:.2f} s)")
        self.pump_for_seconds(pump_id, seconds)

    def pump_all_for_ml(self, volume_ml: float):
        # nacheinander alle Pumpen
        for pid in self.pump_pins.keys():
            self.pump_for_ml(pid, volume_ml)

    def all_off(self):
        for pid in self.pump_pins.keys():
            pin = self.pump_pins[pid]
            GPIO.output(pin, RELAY_INACTIVE_STATE)


class Machine:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(PIN_STATUS_LED, GPIO.OUT)
        GPIO.output(PIN_STATUS_LED, GPIO.LOW)

        self.x_axis = Axis(
            name="SYRINGE",
            pin_step=PIN_SYRINGE_STEP,
            pin_dir=PIN_SYRINGE_DIR,
            pin_en=PIN_SYRINGE_EN,
            pin_endstop=PIN_ENDSTOP_SYRINGE,
            steps_per_mm=STEPS_PER_MM,
            step_delay=STEP_DELAY,
            dir_high_is_positive=True,
            home_towards_positive=False,  # Endstop bei 0
        )

        self.y_axis = Axis(
            name="Y",
            pin_step=PIN_Y_STEP,
            pin_dir=PIN_Y_DIR,
            pin_en=PIN_Y_EN,
            pin_endstop=PIN_ENDSTOP_Y,
            steps_per_mm=STEPS_PER_MM,
            step_delay=STEP_DELAY,
            dir_high_is_positive=True,
            home_towards_positive=False,
        )

        self.z_axis = Axis(
            name="Z",
            pin_step=PIN_Z_STEP,
            pin_dir=PIN_Z_DIR,
            pin_en=PIN_Z_EN,
            pin_endstop=PIN_ENDSTOP_Z,
            steps_per_mm=STEPS_PER_MM,
            step_delay=STEP_DELAY,
            dir_high_is_positive=True,
            home_towards_positive=False,
        )

        self.pumps = PumpController(PUMP_PINS)

    # ------------------- Convenience-Methoden -------------------

    def home_all(self):
        print("[MACHINE] Homing aller Achsen (X,Y,Z auf 0)...")
        self.x_axis.home()
        self.y_axis.home()
        self.z_axis.home()
        print("[MACHINE] Homing fertig – Koordinaten = (0,0,0)")

    def move_to_x_index(self, idx: int):
        target_mm = X_POSITIONS_MM[idx]
        print(f"[MACHINE] X → Index {idx} ({target_mm} mm)")
        self.x_axis.move_to_mm(target_mm)

    def move_to_z_index(self, idx: int):
        target_mm = Z_POSITIONS_MM[idx]
        print(f"[MACHINE] Z → Index {idx} ({target_mm} mm)")
        self.z_axis.move_to_mm(target_mm)

    def move_y_to_cm(self, y_cm: float):
        target_mm = y_cm * 10.0
        print(f"[MACHINE] Y → {y_cm} cm ({target_mm} mm)")
        self.y_axis.move_to_mm(target_mm)

    def move_y_rel_cm(self, delta_cm: float):
        delta_mm = delta_cm * 10.0
        print(f"[MACHINE] Y rel {delta_cm} cm ({delta_mm} mm)")
        self.y_axis.move_mm_relative(delta_mm)