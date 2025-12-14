from pprint import pformat
from itertools import product
from typing import Any, Dict
import time
from scripts.ablauf import starteAblauf #hat bei leyna nicht funktioniert
from .runner import TaskState


def start_process(payload: Dict[str, Any]) -> Dict[str, Any]:
    print("[START] Payload received:\n" + pformat(payload))
    # Hier würde später die echte Verdünnungslogik aufgerufen
    starteAblauf(payload) #hat bei leyna nicht funktioniert
    return {"status": "started"}


def cancel_process(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    print("[CANCEL] Request received:\n" + pformat(payload or {}))
    # Hier später: aktiven Task stoppen, Hardware in sicheren Zustand versetzen

    return {"status": "cancelled"}

def check_factors(data: Dict[str, Any]):
    factors = data.get("factors", [])
    fills = data.get("fills", [])
    rows = data.get("enabledRows", [])
    stock = data.get("stockVolume", None)
    cover = data.get("cover", None)
    grid = data.get("grid", [])

    
    factor1: int = factors.get("2")
    factor2: int = factors.get("1")
    factor3: int = factors.get("0")

    fill1 = fills.get("2")
    fill2 = fills.get("1")
    fill3 = fills.get("0")

    row3active = rows.get("0")
    row2active = rows.get("1")

    #stock volume check
    if stock is None: 
        return (False, "Stock volume is missing")

    #factor and fill checks
    if factor1 is None or (row2active and factor2 is None) or (row3active and factor3 is None):
        return (False, "Factors do not match grid configuration")
    
    if not row2active and factor2 is not None:
        factors.update({"2": None})

    if not row3active and factor3 is not None:
        factors.update({"0": None})

    if row3active:
        fills.update({"2": None, "1": None})
        if fill3 is None:
            return (False, "Fill volume for row 3 is missing")
    if row2active and not row3active:
        fills.update({"2": None, "0": None})
        if fill2 is None:
            return (False, "Fill volume for row 2 is missing")
    if not row2active and not row3active:
        fills.update({"1": None, "0": None})
        if fill1 is None:
            return (False, "Fill volume for row 1 is missing")

    if factor1 > 1 and factor1 <= 10:
        print("Factors are valid")
    else:
        return (False, "Factors are not all valid")
    
    if row2active:
        if factor2 > 1 and factor2 <= 10:
            print("Factors are valid")
        elif factor2 <= 100 and factor2 % 10 == 0:
            print("Factors are valid")
        else:
            return (False, "Factors are not all valid")
    
    
    if row3active:
        if factor3 > 1 and factor3 <= 10:
            print("Factors are valid")
        elif factor2 <= 100 and factor2 % 10 == 0:
            print("Factors are valid")
        elif factor3 <= 1000 and factor3 % 50 == 0:
            print("Factors are valid")
        else:
            return (False, "Factors are not all valid")
    

    #factors not larger than 10 

    # if (row3active and (factor3 / 10)  > factor2):
    #     return (False, "Factor 3 is too large compared to Factor 2")

    # if (row2active and (factor2 / 10)  > factor1):
    #     return (False, "Factor 2 is too large compared to Factor 1")
    

    fa3stammreihe: int = 0
    fa2stammreihe: int = 0
    fa1stammreihe: int = 0

    if row3active and factor3 <= 10:
        fa3stammreihe = 0
    elif row3active and factor3 <= 100 and factor3 / 10 <= factor1:
        fa3stammreihe = 1
    elif row3active and factor3 <= 1000 and factor3 / 100 <= factor2:
        fa3stammreihe = 2
    
    if row2active and factor2 <= 10:
        fa2stammreihe = 0
    elif row2active and factor2 <= 100 and factor2 / 10 <= factor1:
        fa2stammreihe = 1

    if row3active:
        stammmenge1: float = calculating_stocksolution(14, factor1, 1)

        if fa2stammreihe == 0:
            stammmenge2: float = calculating_stocksolution(14, factor2, 1)
        elif fa2stammreihe == 1:
            stammmenge2: float = calculating_stocksolution(14, factor2, factor1)

        if fa3stammreihe == 0:
            stammmenge3: float = calculating_stocksolution(14, factor3, 1)
        elif fa3stammreihe == 1:
            stammmenge3: float = calculating_stocksolution(fill3, factor3, factor1)
        elif fa3stammreihe == 2:
            stammmenge3: float = calculating_stocksolution(fill3, factor3, factor2)
        
        
        verdunnungsmenge3: float = calculating_dilutionsolution(fill3, stammmenge3)
        verdunnungsmenge2: float = calculating_dilutionsolution(14, stammmenge2)
        verdunnungsmenge1: float = calculating_dilutionsolution(14, stammmenge1)

        volumen3 = stammmenge3 + verdunnungsmenge3
        volumen2 = stammmenge2 + verdunnungsmenge2
        volumen1 = stammmenge1 + verdunnungsmenge1
        volumenstock = data.get("stockVolume", None)

        if row3active and fa3stammreihe == 0:
            volumenstock -= stammmenge3
        elif row3active and fa3stammreihe == 1:
            volumen1 -= stammmenge3
        elif row3active and fa3stammreihe == 2:
            volumen2 -= stammmenge3
        
        if row2active and fa2stammreihe == 0:
            volumenstock -= stammmenge2
        elif row2active and fa2stammreihe == 1:
            volumen1 -= stammmenge2

        volumenstock -= stammmenge1
        
        if volumenstock < 2:
            return (False, "Not enough stock solution for all rows")

        info3: Dict[str, Any] = {
            "Reihe": 3,
            "Stammreihe": fa3stammreihe,
            "Stammmenge": stammmenge3,
            "Verduennungsmenge": verdunnungsmenge3,
            "Volumen": volumen3,
            "Verduennung": factor3
        }
        info2: Dict[str, Any] = {
            "Reihe": 2,
            "Stammreihe": fa2stammreihe,
            "Stammmenge": stammmenge2,
            "Verduennungsmenge": verdunnungsmenge2,
            "Volumen": volumen2,
            "Verduennung": factor2
        }
        info1: Dict[str, Any] = {
            "Reihe": 1,
            "Stammreihe": fa1stammreihe,
            "Stammmenge": stammmenge1,
            "Verduennungsmenge": verdunnungsmenge1,
            "Volumen": volumen1,
            "Verduennung": factor1
        }
        data.update({"info3": info3, "info2": info2, "info1": info1})
    elif not row3active and row2active:
        stammmenge1: float = calculating_stocksolution(14, factor1, 1)
        
        if fa2stammreihe == 0:
            stammmenge2: float = calculating_stocksolution(14, factor2, 1)
        elif fa2stammreihe == 1:
            stammmenge2: float = calculating_stocksolution(14, factor2, factor1)

        verdunnungsmenge2: float = calculating_dilutionsolution(fill2, stammmenge2)
        verdunnungsmenge1: float = calculating_dilutionsolution(14, stammmenge1)

        volumen2 = stammmenge2 + verdunnungsmenge2
        volumen1 = stammmenge1 + verdunnungsmenge1
        volumenstock = data.get("stockVolume", None)

        
        if row2active and fa2stammreihe == 0:
            volumenstock -= stammmenge2
        elif row2active and fa2stammreihe == 1:
            volumen1 -= stammmenge2

        volumenstock -= stammmenge1
        
        if volumenstock < 2:
            return (False, "Not enough stock solution for all rows")
        
        info2: Dict[str, Any] = {
            "Reihe": 2,
            "Stammreihe": fa2stammreihe,
            "Stammmenge": stammmenge2,
            "Verduennungsmenge": verdunnungsmenge2,
            "Volumen": volumen2,
            "Verduennung": factor2
        }
        info1: Dict[str, Any] = {
            "Reihe": 1,
            "Stammreihe": fa1stammreihe,
            "Stammmenge": stammmenge1,
            "Verduennungsmenge": verdunnungsmenge1,
            "Volumen": volumen1,
            "Verduennung": factor1
        }
        data.update({"info2": info2, "info1": info1})
    else:
        stammmenge1: float = calculating_stocksolution(fill1, factor1, 1)
        verdunnungsmenge1: float = calculating_dilutionsolution(fill1, stammmenge1)

        volumen1 = stammmenge1 + verdunnungsmenge1
        volumenstock = data.get("stockVolume", None)

        volumenstock -= stammmenge1
        
        if volumenstock < 2:
            return (False, "Not enough stock solution for all rows")

        info1: Dict[str, Any] = {
            "Reihe": 1,
            "Stammreihe": fa1stammreihe,
            "Stammmenge": stammmenge1,
            "Verduennungsmenge": verdunnungsmenge1,
            "Volumen": volumen1,
            "Verduennung": factor1
        }
        data.update({"info1": info1})

    return (True, "All checks passed")
        
    
    


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


def calculating_stocksolution(endsolutionamount: int, dilutionfactor: int, alreadyusedfactor: int):
    base_amount = endsolutionamount / (dilutionfactor / alreadyusedfactor)
    return base_amount

def calculating_dilutionsolution(endsolutionamount: int, base_amount: int):
    dilution = endsolutionamount - base_amount
    return dilution


