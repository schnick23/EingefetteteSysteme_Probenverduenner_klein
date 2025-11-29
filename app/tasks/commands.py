from pprint import pformat
from itertools import product
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
    
    factor1 = factors.get("1")
    factor2 = factors.get("2")
    factor3 = factors.get("0")

    row3off = (grid[0][0]==False and grid[0][1]==False and grid[0][2]==False and grid[0][3]==False and grid[0][4]==False)
    row2off = (grid[1][0]==False and grid[1][1]==False and grid[1][2]==False and grid[1][3]==False and grid[1][4]==False)

    if factor1 is None or (row3off != False and factor3 is not None) or (row3off != True and factor3 is None) or (row2off != False and factor2 is not None) or (row2off != True and factor2 is None):
        return (False, "Factors do not match grid configuration")
    
    if factor1 > 1 and factor1 <= 10:
        print("Factors are valid")
    else:
        return (False, "Factors are not all valid")
    
    if factor2 is not None:
        if factor2 > 1 and factor2 <= 10:
            print("Factors are valid")
        elif factor2 <= 100 and factor2 % 10 == 0:
            print("Factors are valid")
        else:
            return (False, "Factors are not all valid")
    else:
        print("Factor2 is None, skipping validation")
        return (True, "OK")
    
    if factor3 is not None:
        if factor3 > 1 and factor3 <= 10:
            print("Factors are valid")
        elif factor2 <= 100 and factor2 % 10 == 0:
            print("Factors are valid")
        elif factor3 <= 1000 and factor3 % 50 == 0:
            print("Factors are valid")
        else:
            return (False, "Factors are not all valid")
    else:
        print("Factor3 is None, skipping validation")
        return (True, "OK")


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


def steps(dilutionfactor: int) -> int:
    """Berechnet die Anzahl der Verdünnungsschritte basierend auf dem Verdünnungsfaktor."""
    count = 0
    factor = dilutionfactor
    while factor > 9:
        factor %= 10
        count += 1
    return count


def prime_factors(dilutionfactor: int) -> list[int]:
    factors = []
    d = 2

    # solange d*d <= n, prüfen wir Teilbarkeit
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1

    # wenn am Ende n > 1 ist, ist es selbst ein Primfaktor
    if n > 1:
        factors.append(n)

    return factors


def split_into_three_numbers_limited(factors, min_val=2, max_val=19):
    """
    Teilt Faktoren in 3 Gruppen auf → ergibt drei Zahlen a,b,c.
    Bedingungen:
      - jede Zahl > min_val-1 (also ≥2)
      - jede Zahl ≤ max_val
    """
    solutions = set()

    # Für jede mögliche Zuordnung (jede Zahl bekommt Gruppe 0,1,2)
    for assignment in product(range(3), repeat=len(factors)):
        groups = [1, 1, 1]

        for factor, group in zip(factors, assignment):
            groups[group] *= factor

        # Bedingungen prüfen
        if all(min_val <= g <= max_val for g in groups):
            solutions.add(tuple(sorted(groups)))  # sortiert = Duplikate vermeiden

    return sorted(solutions)


def calculating_solution(endproduct: int, dilutionfactor: int):
    base_amount = endproduct / dilutionfactor
    return base_amount

def calculating_solution(endproduct: int, base_amount: int):
    dilution = endproduct - base_amount
    return dilution