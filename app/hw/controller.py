from abc import ABC, abstractmethod
from typing import Dict, Any
import time

class HardwareError(Exception):
    pass

class HardwareInterface(ABC):
    @abstractmethod
    def initialize(self) -> None:
        ...

    @abstractmethod
    def start_pump(self, pump_id: str, speed: float = 1.0) -> None:
        ...

    @abstractmethod
    def stop_pump(self, pump_id: str) -> None:
        ...

    @abstractmethod
    def set_valve(self, valve_id: str, position: int) -> None:
        ...

    @abstractmethod
    def read_sensor(self, sensor_id: str) -> float:
        ...

class MockHardware(HardwareInterface):
    def __init__(self):
        self._pumps = {}
        self._valves = {}
        self._sensors = {"temp": 22.5, "level": 0.0}

    def initialize(self) -> None:
        pass

    def start_pump(self, pump_id: str, speed: float = 1.0) -> None:
        self._pumps[pump_id] = speed

    def stop_pump(self, pump_id: str) -> None:
        self._pumps.pop(pump_id, None)

    def set_valve(self, valve_id: str, position: int) -> None:
        self._valves[valve_id] = position

    def read_sensor(self, sensor_id: str) -> float:
        base = self._sensors.get(sensor_id, 0.0)
        # simple fluctuation
        return base + (time.time() % 5) * 0.01

    def debug_state(self) -> Dict[str, Any]:
        return {"pumps": self._pumps, "valves": self._valves}
