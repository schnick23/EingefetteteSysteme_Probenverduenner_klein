from . import HubTisch
from . import LinearFuehrung
from . import pumpenSteuerung
from . import Spritzkopf
import json
from .motorcontroller import Axis
from pathlib import Path
import RPi.GPIO as GPIO
from . import ablaeufe

def starteAblauf(payload):
    try:
        # Pfad zur config.json relativ zum aktuellen Skript ermitteln
        config_path = Path(__file__).resolve().parent / "config.json"

        # config öffnen und laden
        with open(config_path, "r", encoding="utf-8") as config_file:
            config = json.load(config_file)

        # pumpen initialisieren
        pump1= config["gpio"]["relais"]["relais1"]
        pump2= config["gpio"]["relais"]["relais2"]
        pump3= config["gpio"]["relais"]["relais3"]
        pump4= config["gpio"]["relais"]["relais4"]
        pump5= config["gpio"]["relais"]["relais5"]
        relais6= config["gpio"]["relais"]["relais6"]
        relais7= config["gpio"]["relais"]["relais7"]
        relais8= config["gpio"]["relais"]["relais8"]
        pumpen_controller = pumpenSteuerung.PumpenSteuerung(pump1, pump2, pump3, pump4, pump5, relais6, relais7, relais8)

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

        # Abläufe ausführen
        ablaeufe.nullpositioniereSystem(hubtisch_controller, linearfuehrung_controller, spritzkopf_controller)
        ablaeufe.ersteReinigung(hubtisch_controller, linearfuehrung_controller, spritzkopf_controller, pumpen_controller)

    except Exception as e:
        print(f"\n=== SYSTEM: FEHLER AUFGETRETEN ===\n{e}")
    finally:
        print("\n=== SYSTEM: PROGRAMM BEENDET ===")
        GPIO.cleanup()