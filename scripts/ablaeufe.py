import HubTisch
import LinearFuehrung
import pumpenSteuerung
import Spritzkopf
import json
from motorcontroller import Axis
from pathlib import Path
import RPi.GPIO as GPIO

def nullpositioniereSystem(hubtisch_controller, linearfuehrung_controller, spritzkopf_controller):
    print("\n=== SYSTEM: NULLPOSITIONIERE ALLE ACHSEN ===")
    hubtisch_controller.home()
    linearfuehrung_controller.home()
    linearfuehrung_controller.move_linear_to_index(7)  # Abfallbehälter
    hubtisch_controller.move_hub_to_cleaning()
    spritzkopf_controller.home() # Spritzkopf leeren
    hubtisch_controller.home()
    linearfuehrung_controller.front()  # Anfangsposition
    print("\n=== SYSTEM: NULLPOSITIONIERUNG ABGESCHLOSSEN ===")

def ersteReinigung(hubtisch_controller, linearfuehrung_controller, spritzkopf_controller, pumpen_controller):
    print("\n=== SYSTEM: ERSTE REINIGUNGSDURCHFÜHRUNG ===")
    nullpositioniereSystem()
    linearfuehrung_controller.move_linear_to_index(7)  # abfallbehälter
    hubtisch_controller.move_hub_to_cleaning()
    pumpen_controller.all_pump_ml(200.0)  # SCHLAUCHVOLUMEN ERMITTELN UND ANPASSEN
    hubtisch_controller.home()
    linearfuehrung_controller.move_linear_to_index(6)  # Reinigungsbehälter
    spritzkopf_controller.set_volume_ml(0.4)  # Luftblase aufziehen
    hubtisch_controller.move_hub_to_top()
    pumpen_controller.all_pump_ml(5.0)  # Alle Pumpen 5 ml
    spritzkopf_controller.set_volume_ml(2.0)  # Spritzkopf aufziehen
    hubtisch_controller.home()
    linearfuehrung_controller.move_linear_to_index(7)  # Abfallbehälter
    hubtisch_controller.move_hub_to_cleaning()
    spritzkopf_controller.home()  # Spritzkopf leeren
    hubtisch_controller.home()
    linearfuehrung_controller.move_linear_to_index(6)  # Renigungsbehälter
    spritzkopf_controller.set_volume_ml(0.4)  # Luftblase aufziehen
    hubtisch_controller.move_hub_to_top()
    pumpen_controller.all_pump_ml(5.0)  # DARAUF SCHAUEN; Evtl. mehr ml pumpen
    spritzkopf_controller.set_volume_ml(2.0)  # Spritzkopf aufziehen
    hubtisch_controller.home()
    linearfuehrung_controller.move_linear_to_index(7)  # Abfallbehälter
    hubtisch_controller.move_hub_to_cleaning()
    spritzkopf_controller.home() # Spritzkopf leeren
    hubtisch_controller.home()
    linearfuehrung_controller.move_linear_to_index(1)  # Anfangsposition
    print("\n=== SYSTEM: REINIGUNG ABGESCHLOSSEN ===")

def Verdünnen(hubtisch_controller, linearfuehrung_controller, spritzkopf_controller, pumpen_controller, Stammreihe: int, StammLsg: float, VerdLsg: float):
    print("\n=== SYSTEM: PROBENVERDÜNNUNG DURCHFÜHREN ===")
    hubtisch_controller.home()
    linearfuehrung_controller.move_linear_to_index(Stammreihe)  # Verdünnungsreihe
    spritzkopf_controller.set_volume_ml(0.4)
    hubtisch_controller.move_hub_to_top()
    spritzkopf_controller.set_volume_ml(StammLsg + 0.4)  # Spritzkopf aufziehen
    hubtisch_controller.home()
    linearfuehrung_controller.move_linear_to_index(Stammreihe + 1)  # Verdünnungsreihe
    hubtisch_controller.move_hub_to_top()
    spritzkopf_controller.set_volume_ml(0)  # Spritzkopf leeren
    pumpen_controller.all_pump_ml(VerdLsg)  # Alle Pumpen Verdünnungslösung
    hubtisch_controller.home()
    print("\n=== SYSTEM: PROBENVERDÜNNUNG ABGESCHLOSSEN ===")

def ZwischenReinigung(hubtisch_controller, linearfuehrung_controller, spritzkopf_controller, Stammreihe: int, StammLsg: float):
    print("\n=== SYSTEM: ZWISCHENREINIGUNG DURCHFÜHREN ===")
    for cycle in range(1,2):
        print(f"\n--- REINIGUNGSZYKLUS {cycle} ---")
        hubtisch_controller.home()
        spritzkopf_controller.set_volume_ml(0.4)  # Luftblase aufziehen
        linearfuehrung_controller.move_linear_to_index(Stammreihe)
        hubtisch_controller.move_hub_to_top()
        spritzkopf_controller.set_volume_ml(StammLsg + 0.9)  # Spritzkopf aufziehen (Stammlösungsmenge + 0.5 + Luftblase)
        hubtisch_controller.home()
        linearfuehrung_controller.move_linear_to_index(7)  # Abfallbehälter
        hubtisch_controller.move_hub_to_cleaning()
        spritzkopf_controller.home() # Spritzkopf leeren
    hubtisch_controller.home()
    print("\n=== SYSTEM: ZWISCHENREINIGUNG ABGESCHLOSSEN ===")