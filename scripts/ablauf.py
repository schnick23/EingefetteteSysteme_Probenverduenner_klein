import HubTisch
import LinearFuehrung
import pumpenSteuerung
import Spritzkopf
import json
from motorcontroller import Axis
from pathlib import Path
import RPi.GPIO as GPIO
import ablaeufe
from simulation_mode import enable_simulation, is_simulation

def entferneAbdeckungAblauf(simulation=False):
    """
    Entfernt die Abdeckung: Hubtisch nach unten, Linear nach hinten.
    """
    if simulation:
        enable_simulation()
        
    try:
        config_path = Path(__file__).resolve().parent / "config.json"
        with open(config_path, "r", encoding="utf-8") as config_file:
            config = json.load(config_file)

        # hubtisch initialisieren
        hub_step= config["gpio"]["stepper_motors"]["hub"]["step_pin"]
        hub_dir= config["gpio"]["stepper_motors"]["hub"]["dir_pin"]
        hub_en= config["gpio"]["stepper_motors"]["hub"]["en_pin"]
        hub_endtaster = config["gpio"]["endstops"]["hub"]
        hub_axis = Axis("Hubtisch_Achse", hub_step, hub_dir, hub_en)
        hubtisch_controller = HubTisch.HubTisch(hub_axis, hub_endtaster)

        # linearführung initialisieren
        lin_step= config["gpio"]["stepper_motors"]["linear"]["step_pin"]
        lin_dir= config["gpio"]["stepper_motors"]["linear"]["dir_pin"]
        lin_en= config["gpio"]["stepper_motors"]["linear"]["en_pin"]
        lin_endtaster_hinten = config["gpio"]["endstops"]["linear_hinten"]
        lin_axis = Axis("Linear_Achse", lin_step, lin_dir, lin_en)
        linearfuehrung_controller = LinearFuehrung.LinearFuehrung(lin_axis, endstop_pin_hinten=lin_endtaster_hinten)

        # Abdeckung entfernen
        ablaeufe.entferneAbdeckung(hubtisch_controller, linearfuehrung_controller)

    except Exception as e:
        print(f"\n=== SYSTEM: FEHLER AUFGETRETEN ===\n{e}")
        GPIO.cleanup()
    except KeyboardInterrupt:
        print("\n=== SYSTEM: PROGRAMM ABBRUCH DURCH BENUTZER ===")
        GPIO.cleanup()
    finally:
        GPIO.cleanup()

def resetSystemAblauf(simulation=False):
    """
    Reset: Nullpositionierung und Pumpen füllen.
    """
    if simulation:
        enable_simulation()
        
    try:
        config_path = Path(__file__).resolve().parent / "config.json"
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
        pumpen_controller = pumpenSteuerung.Pumpen(pump1, pump2, pump3, pump4, pump5, relais6, relais7, relais8)

        # hubtisch initialisieren
        hub_step= config["gpio"]["stepper_motors"]["hub"]["step_pin"]
        hub_dir= config["gpio"]["stepper_motors"]["hub"]["dir_pin"]
        hub_en= config["gpio"]["stepper_motors"]["hub"]["en_pin"]
        hub_endtaster = config["gpio"]["endstops"]["hub"]
        hub_axis = Axis("Hubtisch_Achse", hub_step, hub_dir, hub_en)
        hubtisch_controller = HubTisch.HubTisch(hub_axis, hub_endtaster)

        # linearführung initialisieren
        lin_step= config["gpio"]["stepper_motors"]["linear"]["step_pin"]
        lin_dir= config["gpio"]["stepper_motors"]["linear"]["dir_pin"]
        lin_en= config["gpio"]["stepper_motors"]["linear"]["en_pin"]
        lin_endtaster_hinten = config["gpio"]["endstops"]["linear_hinten"]
        lin_axis = Axis("Linear_Achse", lin_step, lin_dir, lin_en)
        linearfuehrung_controller = LinearFuehrung.LinearFuehrung(lin_axis, endstop_pin_hinten=lin_endtaster_hinten)

        # spritzkopf initialisieren
        syr_step= config["gpio"]["stepper_motors"]["syringe"]["step_pin"]
        syr_dir= config["gpio"]["stepper_motors"]["syringe"]["dir_pin"]
        syr_en= config["gpio"]["stepper_motors"]["syringe"]["en_pin"]
        syr_axis = Axis("Spritzkopf_Achse", syr_step, syr_dir, syr_en, home_towards_positive=False)
        syr_endtaster_left = config["gpio"]["endstops"]["syringe_links"]
        syr_endtaster_right = config["gpio"]["endstops"]["syringe_rechts"]
        syr_steps_per_ml = config["positions"]["syringe"]["steps_per_ml"]
        syr_max_volume_ml = config["positions"]["syringe"]["max_volume_ml"]
        spritzkopf_controller = Spritzkopf.SyringeHead(syr_axis, endstop_pin_links=syr_endtaster_left, endstop_pin_rechts=syr_endtaster_right, max_volume_ml=syr_max_volume_ml, steps_per_ml=syr_steps_per_ml)

        # Reset durchführen
        ablaeufe.resetSystem(hubtisch_controller, linearfuehrung_controller, spritzkopf_controller, pumpen_controller)

    except Exception as e:
        print(f"\n=== SYSTEM: FEHLER AUFGETRETEN ===\n{e}")
        GPIO.cleanup()
    except KeyboardInterrupt:
        print("\n=== SYSTEM: PROGRAMM ABBRUCH DURCH BENUTZER ===")
        GPIO.cleanup()
    finally:
        GPIO.cleanup()

def starteAblauf(payload, simulation=False, report=None):
    """
    Startet den Verdünnungsablauf.
    
    Args:
        payload: Dictionary mit Prozess-Parametern
        simulation: Wenn True, wird nur simuliert ohne echte Hardware-Ansteuerung
    """
    if simulation:
        enable_simulation()
        
    def _report(msg: str, pct: int | None = None):
        if report:
            try:
                report(msg, pct)
            except Exception:
                pass

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
        pumpen_controller = pumpenSteuerung.Pumpen(pump1, pump2, pump3, pump4, pump5, relais6, relais7, relais8)

        # hubtisch initialisieren
        hub_step= config["gpio"]["stepper_motors"]["hub"]["step_pin"]
        hub_dir= config["gpio"]["stepper_motors"]["hub"]["dir_pin"]
        hub_en= config["gpio"]["stepper_motors"]["hub"]["en_pin"]
        hub_endtaster = config["gpio"]["endstops"]["hub"]
        hub_axis = Axis("Hubtisch_Achse", hub_step, hub_dir, hub_en)
        hubtisch_controller = HubTisch.HubTisch(hub_axis, hub_endtaster)

        # linearführung initialisieren
        lin_step= config["gpio"]["stepper_motors"]["linear"]["step_pin"]
        lin_dir= config["gpio"]["stepper_motors"]["linear"]["dir_pin"]
        lin_en= config["gpio"]["stepper_motors"]["linear"]["en_pin"]
        lin_endtaster_hinten = config["gpio"]["endstops"]["linear_hinten"]
        lin_delay = config['axes']['step_delay_lin']
        lin_axis = Axis("Linear_Achse", lin_step, lin_dir, lin_en, run_delay=lin_delay)
        linearfuehrung_controller = LinearFuehrung.LinearFuehrung(lin_axis, endstop_pin_hinten=lin_endtaster_hinten)

        # spritzkopf initialisieren
        syr_step= config["gpio"]["stepper_motors"]["syringe"]["step_pin"]
        syr_dir= config["gpio"]["stepper_motors"]["syringe"]["dir_pin"]
        syr_en= config["gpio"]["stepper_motors"]["syringe"]["en_pin"]
        syr_axis = Axis("Spritzkopf_Achse", syr_step, syr_dir, syr_en, home_towards_positive=False)
        syr_endtaster_left = config["gpio"]["endstops"]["syringe_links"]
        syr_endtaster_right = config["gpio"]["endstops"]["syringe_rechts"]
        syr_steps_per_ml = config["positions"]["syringe"]["steps_per_ml"]
        syr_max_volume_ml = config["positions"]["syringe"]["max_volume_ml"]
        spritzkopf_controller = Spritzkopf.SyringeHead(syr_axis, endstop_pin_links=syr_endtaster_left, endstop_pin_rechts=syr_endtaster_right, max_volume_ml=syr_max_volume_ml, steps_per_ml=syr_steps_per_ml)
                                                    

        # Abläufe ausführen (Reihenfolge: Nullpositionierung → Erste Reinigung → pro Reihe: Zwischenreinigung ×2 → Verdünnen)
        _report("Nullpositioniere System…", 5)
        ablaeufe.nullpositioniereSystem(hubtisch_controller, linearfuehrung_controller, spritzkopf_controller)

        _report("Erste Reinigung…", 10)
        ablaeufe.ersteReinigung(hubtisch_controller, linearfuehrung_controller, spritzkopf_controller, pumpen_controller)
        # Iteriere über die Reihen 1 bis 3 (Row 0 ist Stammlösung)
        for i in range(1, 4):
            row_key = str(i)
            # Prüfen ob Reihe aktiviert ist (Keys können str oder int sein)
            enabled_rows = payload.get('enabledRows', {})
            is_enabled = enabled_rows.get(row_key) or enabled_rows.get(i)
            
            if is_enabled:
                info_key = f"info{i}"
                info = payload.get(info_key)
                if not info:
                    print(f"Warnung: Keine Info für Reihe {i} gefunden.")
                    continue
                
                stamm_reihe = int(info.get('Stammreihe', None))
                ziel_reihe = int(info.get('Reihe', None))
                stamm_lsg = float(info.get('Stammmenge', 0))
                verd_lsg = float(info.get('Verduennungsmenge', 0))
                
                # Aktive Pumpen für diese Reihe ermitteln
                active_pumps = []
                grid = payload.get('grid', [])
                global_active_pumps = payload.get('activePumps', {})
                
                # Wir gehen davon aus, dass es 5 Spalten/Pumpen gibt
                for col in range(5): 
                    pump_id = col + 1
                    # Globaler Pumpen-Status
                    pump_active = global_active_pumps.get(pump_id) or global_active_pumps.get(str(pump_id))
                    
                    # Grid-Status für dieses spezifische Well (Reihe, Spalte)
                    # Mapping: GUI hat Reihen 0..2 (oben→unten), letzte Reihe (index rows-1) ist Stammlösung.
                    # Für i=1..3 (1=unterste Verdünnungsreihe) gilt: grid_row_index = (len(grid)-1) - i
                    well_active = False
                    grid_row_index = (len(grid) - 1) - i if isinstance(grid, list) and len(grid) >= 4 else None
                    if grid_row_index is not None and grid_row_index >= 0:
                        if grid_row_index < len(grid) and col < len(grid[grid_row_index]):
                            well_active = grid[grid_row_index][col]
                    
                    # Pumpe nur aktivieren, wenn global AN und Well im Grid AN
                    if pump_active and well_active:
                        active_pumps.append(pump_id)
                
                print(f"Starte Verdünnung für Reihe.")
                
                
                _report("Zwischenreinigung…", 15 + i*20)
                # Zwischenreinigung durchführen
                ablaeufe.ZwischenReinigung(
                    hubtisch_controller, 
                    linearfuehrung_controller, 
                    spritzkopf_controller, 
                    Stammreihe=stamm_reihe, 
                    StammLsg=stamm_lsg
                )

                _report("Zwischenreinigung…", 18 + i*20)
                ablaeufe.ZwischenReinigung(
                    hubtisch_controller, 
                    linearfuehrung_controller, 
                    spritzkopf_controller, 
                    Stammreihe=stamm_reihe, 
                    StammLsg=stamm_lsg
                )

                _report(f"Verdünnung Reihe {ziel_reihe} (von {stamm_reihe})…", 20 + i*20)
                ablaeufe.Verduennen(
                    hubtisch_controller, 
                    linearfuehrung_controller, 
                    spritzkopf_controller, 
                    pumpen_controller, 
                    Stammreihe=stamm_reihe, 
                    Reihe=ziel_reihe, 
                    StammLsg=stamm_lsg, 
                    VerdLsg=verd_lsg, 
                    aktivePumpe=active_pumps
                )

        # Abschlussposition abhängig von 'cover'
        try:
            if payload.get('cover'):
                _report("Abdecken…", 95)
                linearfuehrung_controller.move_linear_to_index(1)
                hubtisch_controller.move_hub_to_cover()
            else:
                _report("Fahre in Ausgangsposition…", 95)
                hubtisch_controller.home()
                linearfuehrung_controller.home()
        except Exception:
            pass

        pumpen_controller.fill_all_pumps(False)  # Am Ende alle Pumpen füllen
        _report("Fertig", 100)

    except Exception as e:
        print(f"\n=== SYSTEM: FEHLER AUFGETRETEN ===\n{e}")
        GPIO.cleanup()
    except KeyboardInterrupt:
        print("\n=== SYSTEM: PROGRAMM ABBRUCH DURCH BENUTZER ===")
        GPIO.cleanup()
    finally:
        print("\n=== SYSTEM: PROGRAMM BEENDET ===")
        GPIO.cleanup()