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
