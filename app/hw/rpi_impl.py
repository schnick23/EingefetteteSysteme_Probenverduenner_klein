from typing import Any
try:
    from gpiozero import LED  # Platzhalter für echte Aktoren
except ImportError:  # Falls lokal ohne Pi
    LED = None  # type: ignore

from .controller import HardwareInterface, HardwareError

class RPiHardware(HardwareInterface):
    def __init__(self):
        self._initialized = False
        self._pump_led = None

    def initialize(self) -> None:
        if LED is None:
            raise HardwareError("gpiozero nicht verfügbar – auf einem Raspberry Pi ausführen")
        # Beispiel: LED als Stellvertreter für Pumpe
        self._pump_led = LED(17)  # type: ignore
        self._initialized = True

    def start_pump(self, pump_id: str, speed: float = 1.0) -> None:
        if not self._initialized:
            raise HardwareError("Hardware nicht initialisiert")
        if self._pump_led:
            self._pump_led.on()

    def stop_pump(self, pump_id: str) -> None:
        if self._pump_led:
            self._pump_led.off()

    def set_valve(self, valve_id: str, position: int) -> None:
        # TODO: Implementieren abhängig vom Ventiltyp
        pass

    def read_sensor(self, sensor_id: str) -> float:
        # TODO: Implementieren (ADC etc.)
        return 0.0


def get_hardware() -> HardwareInterface:
    hw = RPiHardware()
    hw.initialize()
    return hw
