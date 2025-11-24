from pprint import pformat
from typing import Any, Dict
import time

from .runner import TaskState


def start_process(payload: Dict[str, Any]) -> Dict[str, Any]:
    print("[START] Payload received:\n" + pformat(payload))
    # Hier würde später die echte Verdünnungslogik aufgerufen
    return {"status": "started"}


def cancel_process(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    print("[CANCEL] Request received:\n" + pformat(payload or {}))
    # Hier später: aktiven Task stoppen, Hardware in sicheren Zustand versetzen
    return {"status": "cancelled"}

def check_factors(data: Dict[str, Any]):
    factors = data.get("factors", [])
    grid = data.get("grid", [])
    
    factor1 = factors.get("2")
    factor2 = factors.get("1")
    factor3 = factors.get("0")

    if factor1 is None or (grid[0][0] == False and factor3 is not None) or (grid[0][0] == True and factor3 is None) or (grid[1][0] == False and factor2 is not None) or (grid[1][0] == True and factor2 is None):
        print("Factors do not match grid configuration")
        return False
    
    if factor1 > 1 and factor1 <= 10:
        print("Factors are valid")
    else:
        print("Factors are not valid")
        return False
    
    if factor2 is not None:
        if factor2 > 1 and factor2 <= 10:
            print("Factors are valid")
        elif factor2 <= 100 and factor2 % 10 == 0:
            print("Factors are valid")
        else:
            print("Factors are not valid")
            return False
    else:
        print("Factor2 is None, skipping validation")
        return True
    
    if factor3 is not None:
        if factor3 > 1 and factor3 <= 10:
            print("Factors are valid")
        elif factor2 <= 100 and factor2 % 10 == 0:
            print("Factors are valid")
        elif factor3 <= 1000 and factor3 % 50 == 0:
            print("Factors are valid")
        else:
            print("Factors are not valid")
            return False
    else:
        print("Factor3 is None, skipping validation")
        return True


def simulate_workflow(state: TaskState, payload: Dict[str, Any] | None = None) -> None:
    steps = [
        "Initialisiere Hardware",
        "Prüfe Sensoren",
        "Setze Ventile",
        "Starte Pumpe",
        "Messe Volumen",
        "Mische Lösungen",
        "Warte auf Stabilisierung",
        "Stoppe Pumpe",
        "Schreibe Protokoll",
        "Fertig"
    ]
    total = len(steps)
    for i, title in enumerate(steps, start=1):
        if state.cancel_requested:
            state.state = "stopped"
            state.message = "Abgebrochen"
            return
        state.message = title
        state.progress = int(i / total * 100)
        # Dummy-Laufzeit pro Schritt mit feingranularer Cancel-Prüfung
        for _ in range(20):
            if state.cancel_requested:
                state.state = "stopped"
                state.message = "Abgebrochen"
                return
            time.sleep(0.1)
    # Der Runner setzt state.state am Ende auf finished, solange keine Exception geworfen wird
