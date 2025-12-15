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
    linearfuehrung_controller.home()  # Anfangsposition
    print("\n=== SYSTEM: NULLPOSITIONIERUNG ABGESCHLOSSEN ===")

def ersteReinigung(hubtisch_controller, linearfuehrung_controller, spritzkopf_controller, pumpen_controller):
    print("\n=== SYSTEM: ERSTE REINIGUNGSDURCHFÜHRUNG ===")
    linearfuehrung_controller.move_linear_to_index(7)  # abfallbehälter
    hubtisch_controller.move_hub_to_top()
    pumpen_controller.fill_all_pumps()  # SCHLAUCHVOLUMEN ERMITTELN UND ANPASSEN
    hubtisch_controller.home()
    linearfuehrung_controller.move_linear_to_index(6)  # Reinigungsbehälter
    spritzkopf_controller.go_to_volume(1)  # Luftblase aufziehen
    hubtisch_controller.move_hub_to_top()
    pumpen_controller.fill_all_pumps()  # Reinigungsbehälter füllen
    spritzkopf_controller.aspirate(2.0)  # Spritzkopf aufziehen
    hubtisch_controller.home()
    linearfuehrung_controller.move_linear_to_index(7)  # Abfallbehälter
    hubtisch_controller.move_hub_to_cleaning()
    spritzkopf_controller.home()  # Spritzkopf leeren
    hubtisch_controller.home()
    linearfuehrung_controller.move_linear_to_index(6)  # Renigungsbehälter
    spritzkopf_controller.go_to_volume(1)  # Luftblase aufziehen
    hubtisch_controller.move_hub_to_top()
    spritzkopf_controller.aspirate(2.0)  # Spritzkopf aufziehen
    hubtisch_controller.home()
    linearfuehrung_controller.move_linear_to_index(7)  # Abfallbehälter
    hubtisch_controller.move_hub_to_cleaning()
    spritzkopf_controller.home() # Spritzkopf leeren
    hubtisch_controller.home()
    linearfuehrung_controller.home()  # Anfangsposition
    print("\n=== SYSTEM: REINIGUNG ABGESCHLOSSEN ===")

def Verduennen(hubtisch_controller, linearfuehrung_controller, spritzkopf_controller, pumpen_controller, Stammreihe: int, Reihe: int, StammLsg: float, VerdLsg: float, aktivePumpe: list):
    print("\n=== SYSTEM: PROBENVERDÜNNUNG DURCHFÜHREN ===")
    hubtisch_controller.home()
    linearfuehrung_controller.move_linear_to_index(Stammreihe)  # Verdünnungsreihe
    spritzkopf_controller.go_to_volume(1) # luftblase aufziehen
    hubtisch_controller.move_hub_to_top()
    spritzkopf_controller.go_to_volume(StammLsg)  # Spritzkopf aufziehen um die Stammlösung ml
    hubtisch_controller.home()
    linearfuehrung_controller.move_linear_to_index(Reihe)  # Verdünnungsreihe
    hubtisch_controller.move_hub_to_top()
    spritzkopf_controller.home()  # Spritzkopf leeren
    pumpen_controller.all_pump_ml(VerdLsg, aktivePumpe)  # Alle Pumpen Verdünnungslösung (die aktiv sind)
    hubtisch_controller.home()
    print("\n=== SYSTEM: PROBENVERDÜNNUNG ABGESCHLOSSEN ===")

def ZwischenReinigung(hubtisch_controller, linearfuehrung_controller, spritzkopf_controller, Stammreihe: int, StammLsg: float):
    print("\n=== SYSTEM: ZWISCHENREINIGUNG DURCHFÜHREN ===")
    hubtisch_controller.home()
    spritzkopf_controller.go_to_volume(1)  # Luftblase aufziehen
    linearfuehrung_controller.move_linear_to_index(Stammreihe)
    hubtisch_controller.move_hub_to_top()
    spritzkopf_controller.go_to_volume(StammLsg + 0.9)  # Spritzkopf aufziehen (Stammlösungsmenge + 0.5 + Luftblase)
    hubtisch_controller.home()
    linearfuehrung_controller.move_linear_to_index(7)  # Abfallbehälter
    hubtisch_controller.move_hub_to_cleaning()
    spritzkopf_controller.home() # Spritzkopf leeren
    hubtisch_controller.home()
    print("\n=== SYSTEM: ZWISCHENREINIGUNG ABGESCHLOSSEN ===")