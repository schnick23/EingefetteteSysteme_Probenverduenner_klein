import time

from LinearFuehrung import move_linear_to_index
from HubTisch import move_hub_to_top, move_hub_to_bottom
from PumpenSteuerung import Pumpen


def run_sequence(linear_axis, hub_axis, pumpen: Pumpen):
    """
    Führt eine komplette definierte Sequenz automatisch aus.
    Die Achsen stammen aus deinen bestehenden Klassen.
    """

    print("\n===============================")
    print("       STARTE SEQUENZ")
    print("===============================")

    # -----------------------------------------
    # 0) SYSTEM IN GRUNDSTELLUNG FAHREN
    # -----------------------------------------
    print("\n--- Kalibriere Grundstellung ---")
    move_linear_to_index(linear_axis, 1)   # LINEAR Position 1 (Start)
    move_hub_to_bottom(hub_axis)           # Hub ganz unten

    # -----------------------------------------
    # 1) Pumpenreinigung
    # -----------------------------------------
    print("\n--- Schritt 1: Pumpenreinigung ---")
    move_linear_to_index(linear_axis, 6)   # Position 6 = Reinigungsbehälter
    move_hub_to_top(hub_axis)              # Z-Position hoch
    pumpen.all_pump_ml(1.0)                # 1 ml pumpen
    move_hub_to_bottom(hub_axis)

    # -----------------------------------------
    # 2) Erste Spritzenreinigung
    # -----------------------------------------
    print("\n--- Schritt 2: Erste Spritzenreinigung ---")
    move_linear_to_index(linear_axis, 5)   # Position 5
    # kleine Y-Bewegung wäre eine zweite Achse – kannst du später erweitern

    move_hub_to_top(hub_axis)              # Z-Position 1 (symbolisch)
    pumpen.all_pump_ml(2.0)                # 2 ml pumpen
    move_hub_to_bottom(hub_axis)

    # -----------------------------------------
    # 3) Rückkehr zur Ausgangsposition
    # -----------------------------------------
    print("\n--- Schritt 3: Zurück zur Grundstellung ---")
    move_linear_to_index(linear_axis, 1)
    move_hub_to_bottom(hub_axis)

    print("\n===============================")
    print("     SEQUENZ BEENDET ✔️")
    print("===============================")
