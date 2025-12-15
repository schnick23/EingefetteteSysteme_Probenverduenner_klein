#!/usr/bin/env python3
"""
Simulation Mode für Hardware-Tests ohne echte GPIO-Ansteuerung.
Alle Hardware-Calls werden durch Print-Statements ersetzt.
"""

# Globales Flag für Simulation
SIMULATION_MODE = False

def enable_simulation():
    """Aktiviert den Simulationsmodus"""
    global SIMULATION_MODE
    SIMULATION_MODE = True
    print("🎭 SIMULATION MODE AKTIVIERT - Keine echte Hardware-Ansteuerung!")

def disable_simulation():
    """Deaktiviert den Simulationsmodus"""
    global SIMULATION_MODE
    SIMULATION_MODE = False
    print("⚙️  SIMULATION MODE DEAKTIVIERT - Echte Hardware wird angesteuert!")

def is_simulation():
    """Prüft, ob Simulationsmodus aktiv ist"""
    return SIMULATION_MODE

def sim_print(message):
    """Print nur im Simulationsmodus"""
    if SIMULATION_MODE:
        print(f"[SIM] {message}")
