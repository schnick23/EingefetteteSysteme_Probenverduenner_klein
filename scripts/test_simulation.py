#!/usr/bin/env python3
"""
Testskript für Simulation Mode
Führt einen kompletten Durchlauf ohne Hardware-Ansteuerung durch.
"""

import json
from ablauf import starteAblauf

# Beispiel-Payload (aus last_payload.json oder manuell)
test_payload = {
    'activePumps': {1: True, 2: True, 3: True, 4: True, 5: True},
    'cover': True,
    'enabledRows': {'0': True, '1': True, '2': True, '3': True},
    'factors': {'0': 1000, '1': 100, '2': 10},
    'fills': {'0': 10, '1': None, '2': None},
    'grid': [
        [True, True, True, True, True],
        [True, True, True, True, True],
        [True, True, True, True, True],
        [True, True, True, True, True]
    ],
    'info1': {
        'Reihe': 1,
        'Stammmenge': 1.4,
        'Stammreihe': 0,
        'Verduennung': 10,
        'Verduennungsmenge': 12.6,
        'Volumen': 12.6
    },
    'info2': {
        'Reihe': 2,
        'Stammmenge': 1.4,
        'Stammreihe': 1,
        'Verduennung': 100,
        'Verduennungsmenge': 12.6,
        'Volumen': 13.0
    },
    'info3': {
        'Reihe': 3,
        'Stammmenge': 1.0,
        'Stammreihe': 2,
        'Verduennung': 1000,
        'Verduennungsmenge': 9.0,
        'Volumen': 10.0
    },
    'stockVolume': 10
}

if __name__ == "__main__":
    print("\n" + "="*60)
    print("SIMULATION MODE TEST")
    print("="*60)
    print("\nStarte Ablauf im Simulationsmodus...")
    print("Keine echte Hardware wird angesteuert!\n")
    
    # Starte mit simulation=True
    starteAblauf(test_payload, simulation=True)
    
    print("\n" + "="*60)
    print("SIMULATION ABGESCHLOSSEN")
    print("="*60)
