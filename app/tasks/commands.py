from pprint import pformat
from itertools import product
from typing import Any, Dict
import time
import sys
import os

# Füge den scripts-Ordner zum Python-Pfad hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../scripts")))

from scripts.ablauf import starteAblauf #hat bei leyna nicht funktioniert
from .runner import TaskState


def start_process(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Nur einmalig Payload in CLI ausgeben
    print("[START] Payload received:\n" + pformat(payload))
    return {"status": "printed"}


def run_real_workflow(state: TaskState, payload: Dict[str, Any]) -> None:
    """Startet den echten Verdünnungsprozess im Hintergrund und aktualisiert Statusmeldungen.
    """
    state.message = "Starte Verdünnungsprozess…"
    state.progress = 1

    def report(msg: str, pct: int | None = None):
        state.message = msg
        if pct is not None:
            try:
                pct_i = int(pct)
                state.progress = max(state.progress, max(0, min(100, pct_i)))
            except Exception:
                pass

    try:
        starteAblauf(payload, simulation=False, report=report)
        state.progress = max(state.progress, 100)
    except Exception as e:
        state.state = "error"
        state.message = f"Fehler: {e}"
        return


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
        return (False, "Stammlösungsvolumen fehlt")

    if stock < 2:
        return (False, "Stammlösungsvolumen zu gering, min. 2ml nötig")
    
    if stock > 14:
        return (False, "Stammlösungsvolumen zu hoch, max. 14ml erlaubt")

    #factor and fill checks
    if factor1 is None or (row2active and factor2 is None) or (row3active and factor3 is None):
        return (False, "Faktoren stimmen nicht mit der Rasterkonfiguration überein")
    
    if not row2active and factor2 is not None:
        factors.update({"2": None})

    if not row3active and factor3 is not None:
        factors.update({"0": None})

    if row3active:
        fills.update({"2": None, "1": None})
        if fill3 is None:
            return (False, "Füllvolumen für Reihe 3 fehlt")
        if fill3 > 14:
            return (False, "Füllvolumen für Reihe 3 zu hoch, max. 14ml erlaubt")
    if row2active and not row3active:
        fills.update({"2": None, "0": None})
        if fill2 is None:
            return (False, "Füllvolumen für Reihe 2 fehlt")
        if fill2 > 14:
            return (False, "Füllvolumen für Reihe 2 zu hoch, max. 14ml erlaubt")
    if not row2active and not row3active:
        fills.update({"1": None, "0": None})
        if fill1 is None:
            return (False, "Füllvolumen für Reihe 1 fehlt")
        if fill1 > 14:
            return (False, "Füllvolumen für Reihe 1 zu hoch, max. 14ml erlaubt")
        
    if factor1 > 1 and factor1 <= 10:
        print("Factors are valid")
    else:
        return (False, "Faktoren sind nicht alle gültig")
    
    if row2active:
        if factor2 > 1 and factor2 <= 10:
            print("Faktoren sind gültig")
        elif factor2 <= 100 and factor2 % 10 == 0:
            print("Faktoren sind gültig")
        else:
            return (False, "Faktoren sind nicht alle gültig")
    
    
    if row3active:
        if factor3 > 1 and factor3 <= 10:
            print("Faktoren sind gültig")
        elif factor2 <= 100 and factor2 % 10 == 0:
            print("Faktoren sind gültig")
        elif factor3 <= 1000 and factor3 % 50 == 0:
            print("Faktoren sind gültig")
        else:
            return (False, "Faktoren sind nicht alle gültig")
    

    #factors not larger than 10 

    # if (row3active and (factor3 / 10)  > factor2):
    #     return (False, "Factor 3 is too large compared to Factor 2")

    # if (row2active and (factor2 / 10)  > factor1):
    #     return (False, "Factor 2 is too large compared to Factor 1")
    

    fa3stammreihe: int = 2
    fa2stammreihe: int = 2
    fa1stammreihe: int = 2

    if row3active and factor3 <= 10:
        fa3stammreihe = 2
    elif row3active and factor3 <= 100 and factor3 / 10 <= factor1:
        fa3stammreihe = 3
    elif row3active and factor3 <= 1000 and factor3 / 10 <= factor2:
        fa3stammreihe = 4
    else:
        return (False, "Keine gültige Stammreihe für Reihe 3 gefunden")
    
    if row2active and factor2 <= 10:
        fa2stammreihe = 2
    elif row2active and factor2 <= 100 and factor2 / 10 <= factor1:
        fa2stammreihe = 3
    else:
        return (False, "Keine gültige Stammreihe für Reihe 2 gefunden")

    if row3active:
        stammmenge1: float = calculating_stocksolution(14, factor1, 1)

        if fa2stammreihe == 2:
            stammmenge2: float = calculating_stocksolution(14, factor2, 1)
        elif fa2stammreihe == 3:
            stammmenge2: float = calculating_stocksolution(14, factor2, factor1)

        if fa3stammreihe == 2:
            stammmenge3: float = calculating_stocksolution(14, factor3, 1)
        elif fa3stammreihe == 3:
            stammmenge3: float = calculating_stocksolution(fill3, factor3, factor1)
        elif fa3stammreihe == 4:
            stammmenge3: float = calculating_stocksolution(fill3, factor3, factor2)
        
        
        verdunnungsmenge3: float = calculating_dilutionsolution(fill3, stammmenge3)
        verdunnungsmenge2: float = calculating_dilutionsolution(14, stammmenge2)
        verdunnungsmenge1: float = calculating_dilutionsolution(14, stammmenge1)

        volumen3 = stammmenge3 + verdunnungsmenge3
        volumen2 = stammmenge2 + verdunnungsmenge2
        volumen1 = stammmenge1 + verdunnungsmenge1
        volumenstock = data.get("stockVolume", None)

        if row3active and fa3stammreihe == 2:
            volumenstock -= ((stammmenge3 * 3) + 1)
        elif row3active and fa3stammreihe == 3:
            volumen1 -= ((stammmenge3 * 3) + 1)
        elif row3active and fa3stammreihe == 4:
            volumen2 -= ((stammmenge3 * 3) + 1)
        
        if row2active and fa2stammreihe == 2:
            volumenstock -= ((stammmenge2 * 3) + 1)
        elif row2active and fa2stammreihe == 3:
            volumen1 -= ((stammmenge2 * 3) + 1)

        volumenstock -= ((stammmenge1 * 3) + 1)
        
        if volumenstock < 2:
            return (False, "Nicht genug Stammlösung für alle Reihen vorhanden, 2ml Reserve nötig")
        
        if volumenstock > 14:
            return (False, "Zu viel Stammlösung nötig, max. 14ml erlaubt")

        info3: Dict[str, Any] = {
            "Reihe": 5,
            "Stammreihe": fa3stammreihe,
            "Stammmenge": stammmenge3,
            "Verduennungsmenge": verdunnungsmenge3,
            "Volumen": volumen3,
            "Verduennung": factor3
        }
        info2: Dict[str, Any] = {
            "Reihe": 4,
            "Stammreihe": fa2stammreihe,
            "Stammmenge": stammmenge2,
            "Verduennungsmenge": verdunnungsmenge2,
            "Volumen": volumen2,
            "Verduennung": factor2
        }
        info1: Dict[str, Any] = {
            "Reihe": 3,
            "Stammreihe": fa1stammreihe,
            "Stammmenge": stammmenge1,
            "Verduennungsmenge": verdunnungsmenge1,
            "Volumen": volumen1,
            "Verduennung": factor1
        }
        data.update({"info3": info3, "info2": info2, "info1": info1})
    elif not row3active and row2active:
        stammmenge1: float = calculating_stocksolution(14, factor1, 1)
        
        if fa2stammreihe == 2:
            stammmenge2: float = calculating_stocksolution(14, factor2, 1)
        elif fa2stammreihe == 3:
            stammmenge2: float = calculating_stocksolution(14, factor2, factor1)

        verdunnungsmenge2: float = calculating_dilutionsolution(fill2, stammmenge2)
        verdunnungsmenge1: float = calculating_dilutionsolution(14, stammmenge1)

        volumen2 = stammmenge2 + verdunnungsmenge2
        volumen1 = stammmenge1 + verdunnungsmenge1
        volumenstock = data.get("stockVolume", None)

        
        if row2active and fa2stammreihe == 0:
            volumenstock -= ((stammmenge2 * 3) + 1)
        elif row2active and fa2stammreihe == 1:
            volumen1 -= ((stammmenge2 * 3) + 1)

        volumenstock -= ((stammmenge1 * 3) + 1)
        
        if volumenstock < 2:
            return (False, "Nicht genug Stammlösung für alle Reihen vorhanden, 2ml Reserve nötig")
        
        if volumenstock > 14:
            return (False, "Zu viel Stammlösung nötig, max. 14ml erlaubt")
        
        info2: Dict[str, Any] = {
            "Reihe": 4,
            "Stammreihe": fa2stammreihe,
            "Stammmenge": stammmenge2,
            "Verduennungsmenge": verdunnungsmenge2,
            "Volumen": volumen2,
            "Verduennung": factor2
        }
        info1: Dict[str, Any] = {
            "Reihe": 3,
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

        volumenstock -= ((stammmenge1 * 3) + 1)
        
        if volumenstock < 2:
            return (False, "Nicht genug Stammlösung für alle Reihen vorhanden, 2ml Reserve nötig")
        
        if volumenstock > 14:
            return (False, "Zu viel Stammlösung nötig, max. 14ml erlaubt")

        info1: Dict[str, Any] = {
            "Reihe": 3,
            "Stammreihe": fa1stammreihe,
            "Stammmenge": stammmenge1,
            "Verduennungsmenge": verdunnungsmenge1,
            "Volumen": volumen1,
            "Verduennung": factor1
        }
        data.update({"info1": info1})

    pump1: bool = grid[3][0]
    pump2: bool = grid[3][1]
    pump3: bool = grid[3][2]
    pump4: bool = grid[3][3]
    pump5: bool = grid[3][4]

    activePumps: Dict[int, bool] = {
            1: pump1,
            2: pump2,
            3: pump3,
            4: pump4,
            5: pump5
        }
    
    data.update({"activePumps": activePumps})

    return (True, "Alle Prüfungen bestanden")
        
    
    


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


