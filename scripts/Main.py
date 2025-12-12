import HubTisch
import LinearFuehrung
import pumpenSteuerung
import Spritzkopf
import json
from motorcontroller import Axis
from pathlib import Path

# Pfad zur config.json relativ zum aktuellen Skript ermitteln
config_path = Path(__file__).resolve().parent / "config.json"

# config öffnen und laden
with open(config_path, "r", encoding="utf-8") as config_file:
    config = json.load(config_file)

# pumpen initialisieren
pump1= config["gpio"]["relay"]["pump_1"]
pump2= config["gpio"]["relay"]["pump_2"]
pump3= config["gpio"]["relay"]["pump_3"]
pump4= config["gpio"]["relay"]["pump_4"]
pump5= config["gpio"]["relay"]["pump_5"]
pumpen_controller = pumpenSteuerung.PumpenSteuerung(pump1, pump2, pump3, pump4, pump5)

# hubtisch initialisieren
hub_step= config["gpio"]["hub"]["step_pin"]
hub_dir= config["gpio"]["hub"]["dir_pin"]
hub_en= config["gpio"]["hub"]["en_pin"]
hub_axis = Axis.Axis("Hubtisch_Achse", hub_step, hub_dir, hub_en)
hubtisch_controller = HubTisch.HubTisch(hub_axis)

# linearführung initialisieren
lin_step= config["gpio"]["linear"]["step_pin"]
lin_dir= config["gpio"]["linear"]["dir_pin"]
lin_en= config["gpio"]["linear"]["en_pin"]
lin_axis = Axis.Axis("Linear_Achse", lin_step, lin_dir, lin_en)
linearfuehrung_controller = LinearFuehrung.LinearFuehrung(lin_axis)

# spritzkopf initialisieren
syr_step= config["gpio"]["syringe"]["step_pin"]
syr_dir= config["gpio"]["syringe"]["dir_pin"]
syr_en= config["gpio"]["syringe"]["en_pin"]
syr_axis = Axis.Axis("Spritzkopf_Achse", syr_step, syr_dir, syr_en)
spritzkopf_controller = Spritzkopf.Spritzkopf(syr_axis)

def nullpositioniereSystem():
    print("\n=== SYSTEM: NULLPOSITIONIERE ALLE ACHSEN ===")
    hubtisch_controller.move_hub_to_bottom()
    linearfuehrung_controller.move_linear_to_index(7)  # Abfallbehälter
    hubtisch_controller.move_hub_to_cleaning()
    spritzkopf_controller.set_volume_ml(0.0)  # Spritzkopf leeren
    hubtisch_controller.move_hub_to_bottom()
    linearfuehrung_controller.move_linear_to_index(1)  # Anfangsposition
    print("\n=== SYSTEM: NULLPOSITIONIERUNG ABGESCHLOSSEN ===")

def ersteReinigung():
    print("\n=== SYSTEM: ERSTE REINIGUNGSDURCHFÜHRUNG ===")
    nullpositioniereSystem()
    linearfuehrung_controller.move_linear_to_index(7)  # abfallbehälter
    hubtisch_controller.move_hub_to_cleaning()
    pumpen_controller.all_pump_ml(200.0)  # SCHLAUCHVOLUMEN ERMITTELN UND ANPASSEN
    hubtisch_controller.move_hub_to_bottom()
    linearfuehrung_controller.move_linear_to_index(6)  # Reinigungsbehälter
    spritzkopf_controller.set_volume_ml(0.4)  # Luftblase aufziehen
    hubtisch_controller.move_hub_to_top()
    pumpen_controller.all_pump_ml(5.0)  # Alle Pumpen 5 ml
    spritzkopf_controller.set_volume_ml(2.0)  # Spritzkopf aufziehen
    hubtisch_controller.move_hub_to_bottom()
    linearfuehrung_controller.move_linear_to_index(7)  # Abfallbehälter
    hubtisch_controller.move_hub_to_cleaning()
    spritzkopf_controller.set_volume_ml(0.0)  # Spritzkopf leeren
    hubtisch_controller.move_hub_to_bottom()
    linearfuehrung_controller.move_linear_to_index(6)  # Renigungsbehälter
    spritzkopf_controller.set_volume_ml(0.4)  # Luftblase aufziehen
    hubtisch_controller.move_hub_to_top()
    pumpen_controller.all_pump_ml(5.0)  # DARAUF SCHAUEN; Evtl. mehr ml pumpen
    spritzkopf_controller.set_volume_ml(2.0)  # Spritzkopf aufziehen
    hubtisch_controller.move_hub_to_bottom()
    linearfuehrung_controller.move_linear_to_index(7)  # Abfallbehälter
    hubtisch_controller.move_hub_to_cleaning()
    spritzkopf_controller.set_volume_ml(0.0)  # Spritzkopf leeren
    hubtisch_controller.move_hub_to_bottom()
    linearfuehrung_controller.move_linear_to_index(1)  # Anfangsposition
    print("\n=== SYSTEM: REINIGUNG ABGESCHLOSSEN ===")

def Verdünnen(Stammreihe: int, StammLsg: float, VerdLsg: float):
    print("\n=== SYSTEM: PROBENVERDÜNNUNG DURCHFÜHREN ===")
    hubtisch_controller.move_hub_to_bottom()
    linearfuehrung_controller.move_linear_to_index(Stammreihe)  # Verdünnungsreihe
    spritzkopf_controller.set_volume_ml(0.4)
    hubtisch_controller.move_hub_to_top()
    spritzkopf_controller.set_volume_ml(StammLsg + 0.4)  # Spritzkopf aufziehen
    hubtisch_controller.move_hub_to_bottom()
    linearfuehrung_controller.move_linear_to_index(Stammreihe + 1)  # Verdünnungsreihe
    hubtisch_controller.move_hub_to_top()
    spritzkopf_controller.set_volume_ml(0)  # Spritzkopf leeren
    pumpen_controller.all_pump_ml(VerdLsg)  # Alle Pumpen Verdünnungslösung
    hubtisch_controller.move_hub_to_bottom()
    print("\n=== SYSTEM: PROBENVERDÜNNUNG ABGESCHLOSSEN ===")

def ZwischenReinigung(Stammreihe: int, StammLsg: float):
    print("\n=== SYSTEM: ZWISCHENREINIGUNG DURCHFÜHREN ===")
    for cycle in range(1,2):
        print(f"\n--- REINIGUNGSZYKLUS {cycle} ---")
        hubtisch_controller.move_hub_to_bottom()
        spritzkopf_controller.set_volume_ml(0.4)  # Luftblase aufziehen
        linearfuehrung_controller.move_linear_to_index(Stammreihe)
        hubtisch_controller.move_hub_to_top()
        spritzkopf_controller.set_volume_ml(StammLsg + 0.9)  # Spritzkopf aufziehen (Stammlösungsmenge + 0.5 + Luftblase)
        hubtisch_controller.move_hub_to_bottom()
        linearfuehrung_controller.move_linear_to_index(7)  # Abfallbehälter
        hubtisch_controller.move_hub_to_cleaning()
        spritzkopf_controller.set_volume_ml(0.0)  # Spritzkopf leeren
    hubtisch_controller.move_hub_to_bottom()
    print("\n=== SYSTEM: ZWISCHENREINIGUNG ABGESCHLOSSEN ===")