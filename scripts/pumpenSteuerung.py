import RPi.GPIO as GPIO
import time
from typing import Iterable, Optional

SECONDS_PER_ML = {
    1: 3.445,
    2: 3.480,
    3: 3.410,
    4: 3.600,
    5: 3.490
}


class Pumpen:
    """
    Steuerung von bis zu 5 Pumpen über ein Relais-Modul.

    - GPIO-Pins sind fest im Dictionary PUMP_PINS hinterlegt.
    - Alle Pumpen werden gleich angesteuert.
    - Über seconds_per_ml wird festgelegt, wie lange eine Pumpe
      für 1 ml laufen muss (Kalibrierwert!).
    """

    # BCM-GPIO-Pins für die 5 Pumpen (Beispielwerte, bitte an dein Board anpassen)
    

    # ANNAHME: Relais ist "active LOW"
    # LOW  = Relais zieht an → Pumpe AN
    # HIGH = Relais aus      → Pumpe AUS
    RELAY_ACTIVE_STATE = GPIO.HIGH
    RELAY_INACTIVE_STATE = GPIO.LOW




    def __init__(self, pump1, pump2, pump3, pump4, pump5, relais6, relais7, relais8):
        """
        seconds_per_ml:
            Wie viele Sekunden muss die Pumpe laufen, um ~1 ml zu fördern?
            → Diesen Wert musst du durch Kalibrieren bestimmen!
        """
        self.seconds_per_ml = SECONDS_PER_ML
        self.PUMP_PINS = {
            1: pump1,
            2: pump2,
            3: pump3,
            4: pump4,
            5: pump5
        }
        self.RELAIS_PINS ={
            6: relais6,
            7: relais7,
            8: relais8
        }

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)


        # Alle Pumpenpins als Ausgang initialisieren und ausschalten
        for pin in self.PUMP_PINS.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, self.RELAY_INACTIVE_STATE)
        for pin in self.RELAIS_PINS.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, self.RELAY_INACTIVE_STATE)



    # ============================
    #  interne Hilfsfunktionen
    # ============================

    def _check_pump_id(self, pump_id: int):
        if pump_id not in self.PUMP_PINS:
            raise ValueError(
                f"Ungültige Pumpen-ID {pump_id}. Erlaubt: {list(self.PUMP_PINS.keys())}"
            )


    # ============================
    #  alle Pumpen
    # ============================

    def _iter_pump_ids(self, pump_ids: Optional[Iterable[int]] = None):
        """Hilfsfunktion: gibt eine Liste von Pumpen-IDs zurück (Standard: alle)."""
        if pump_ids is None:
            pump_ids = self.PUMP_PINS.keys()
        for pid in pump_ids:
            self._check_pump_id(pid)
            yield pid

    def all_on(self, pump_ids: Optional[Iterable[int]] = None):
        """Schaltet alle (oder ausgewählte) Pumpen EIN."""
        for pid in self._iter_pump_ids(pump_ids):
            GPIO.output(self.PUMP_PINS[pid], self.RELAY_ACTIVE_STATE)

    def all_off(self, pump_ids: Optional[Iterable[int]] = None):
        """Schaltet alle (oder ausgewählte) Pumpen AUS."""
        for pid in self._iter_pump_ids(pump_ids):
            GPIO.output(self.PUMP_PINS[pid], self.RELAY_INACTIVE_STATE)

    def all_pump_ml(self, ml: float, pump_ids: list = None):
        """
        Lässt alle (oder eine Auswahl von) Pumpen GLEICHZEITIG dieselbe ml-Menge pumpen.
        Realisiert, indem sie gleichzeitig eingeschaltet werden, gewartet wird
        und dann alle wieder ausgeschaltet werden.
        """
        seconds_per_ml_list list = [
            (pid, self.seconds_per_ml[pid])
            for pid in self._iter_pump_ids(pump_ids)
        ]
        seconds_per_ml_list.sort(key=lambda x: x[1])  # nach Sekunden pro ml sortieren
        self.all_on(pump_ids)
        current_time = 0.0
        for pid, spm in seconds_per_ml_list:
            wait_time = spm * ml
            print(f"Pumpe {pid} pumpt {ml} ml (Dauer: {wait_time:.2f} s)")
            time.sleep(wait_time-current_time)
            GPIO.output(self.PUMP_PINS[pid], self.RELAY_INACTIVE_STATE)
            current_time = spm * ml
            print(f"Pumpe {pid} fertig.")
        self.all_off(self)

    # ============================
    #  Aufräumen
    # ============================

    def cleanup(self):
        """Alle Pumpen ausschalten und GPIO aufräumen."""
        print("Schalte alle Pumpen aus & GPIO.cleanup()...")
        try:
            self.all_off()
        finally:
            GPIO.cleanup()
        print("GPIO cleaned up.")
    
    def changeDir(self, dir: bool): 
        """
            Ändert die Drehrichtung der Pumpen.
            true = vorwärts, false = rückwärts
        """
        
        for pin in self.PUMP_PINS.values():
            GPIO.output(pin, self.RELAY_INACTIVE_STATE)
        if not dir:
            GPIO.output(self.RELAIS_PINS[7], self.RELAY_ACTIVE_STATE)
            time.sleep(0.1)  
            GPIO.output(self.RELAIS_PINS[8], self.RELAY_ACTIVE_STATE)
            time.sleep(0.1)
            GPIO.output(self.RELAIS_PINS[6], self.RELAY_ACTIVE_STATE)
        else:
            GPIO.output(self.RELAIS_PINS[6], self.RELAY_INACTIVE_STATE)
            time.sleep(0.1)  
            GPIO.output(self.RELAIS_PINS[8], self.RELAY_INACTIVE_STATE)
            time.sleep(0.1)
            GPIO.output(self.RELAIS_PINS[7], self.RELAY_INACTIVE_STATE)