import RPi.GPIO as GPIO
import time
from typing import Iterable, Optional

SECONDS_PER_ML = 0.5  # Standardwert, anpassen durch Kalibrieren!


class Pumpen:
    """
    Steuerung von bis zu 5 Pumpen über ein Relais-Modul.

    - GPIO-Pins sind fest im Dictionary PUMP_PINS hinterlegt.
    - Alle Pumpen werden gleich angesteuert.
    - Über seconds_per_ml wird festgelegt, wie lange eine Pumpe
      für 1 ml laufen muss (Kalibrierwert!).
    """

    # BCM-GPIO-Pins für die 5 Pumpen (Beispielwerte, bitte an dein Board anpassen)
    PUMP_PINS = {
        1: 17,
        2: 27,
        3: 22,
        4: 23,
        5: 24,
    }

    # ANNAHME: Relais ist "active LOW"
    # LOW  = Relais zieht an → Pumpe AN
    # HIGH = Relais aus      → Pumpe AUS
    RELAY_ACTIVE_STATE = GPIO.LOW
    RELAY_INACTIVE_STATE = GPIO.HIGH




    def __init__(self):
        """
        seconds_per_ml:
            Wie viele Sekunden muss die Pumpe laufen, um ~1 ml zu fördern?
            → Diesen Wert musst du durch Kalibrieren bestimmen!
        """
        self.seconds_per_ml = SECONDS_PER_ML 

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)


        # Alle Pumpenpins als Ausgang initialisieren und ausschalten
        for pin in self.PUMP_PINS.values():
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
            self.pump_on(pid)

    def all_off(self, pump_ids: Optional[Iterable[int]] = None):
        """Schaltet alle (oder ausgewählte) Pumpen AUS."""
        for pid in self._iter_pump_ids(pump_ids):
            self.pump_off(pid)

    def all_pump_ml(self, ml: float, pump_ids: Optional[Iterable[int]] = None):
        """
        Lässt alle (oder eine Auswahl von) Pumpen GLEICHZEITIG dieselbe ml-Menge pumpen.
        Realisiert, indem sie gleichzeitig eingeschaltet werden, gewartet wird
        und dann alle wieder ausgeschaltet werden.
        """
        seconds = ml * self.seconds_per_ml
        print(f"Alle Pumpen: {ml:.2f} ml → {seconds:.2f} s")

        self.all_on(pump_ids)
        time.sleep(seconds)
        self.all_off(pump_ids)

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

