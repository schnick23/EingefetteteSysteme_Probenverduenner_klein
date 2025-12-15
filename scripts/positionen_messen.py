import HubTisch
import LinearFuehrung
import Spritzkopf
import pumpenSteuerung
import time
import json
import motorcontroller
import RPi.GPIO as GPIO
import os

current = None


axis_steps= {
    "Hubtisch-Achse": 0,
    "Linear-Achse": 0,
    "Spritzkopf-Achse": 0
}


def measure_positions(element):
    steps = 0
    current = element.AXIS.name
    while True:
        try:
            command = input("Mögliche Befehle: \n 'h' - Home \n 'v' - Home Vorne (nur Linear) \n 'w' - Schritte vorwärts \n 's' - Schritte rückwärts \n 'i' - Info aktuelle Position \n 'q' - Beenden \n Eingabe: ")            
            if command.lower() == 'q':
                print(current,steps)
                element.home()
                break
            elif command.lower() == 'hub':
                print(current,axis_steps[current])
                measure_positions(hub_tisch)
            elif command.lower() == 'lin':
                print(current,axis_steps[current])
                measure_positions(linear_fuehrung)
            elif command.lower() == 'syr':
                print(current,axis_steps[current])
                measure_positions(spritzkopf)
            elif command.lower() == 'h':
                element.home()
                axis_steps[current] = 0
                steps = 0
                
            elif command.lower() == 'v' and current == "Linear-Achse":
                element.home_vorne()
                steps = 100000
                axis_steps[current] = 100000
            
            elif command.lower() == 'w':
                front_steps = input("Wie viele Schritte zurückfahren? ")
                try:
                    front_steps = int(front_steps)
                    steps += front_steps
                    element.AXIS._do_step(front_steps, True)
                    axis_steps[current] +=front_steps
                except ValueError:
                    print("Ungültige Eingabe. Bitte eine Zahl eingeben.")
            elif command.lower() == 'i':
                os.system('clear')
                print(f"HubTisch Schritte: {axis_steps["Hubtisch-Achse"]}, Linear Schritte: {axis_steps["Linear-Achse"]}, Spritzkopf Schritte: {axis_steps["Spritzkopf-Achse"]}")
                print(f"Current: {current}")
            elif command.lower() == 'p':
                print(f"Current: {current}, Steps: {steps}")
                while True:
                    try:
                        pumpen_command = input("Welche Pumpe soll laufen? (1-5) oder a oder dir oder 'q' zum Beenden: ")
                        if pumpen_command.lower() == 'q':
                            break
                        if pumpen_command.lower() == 'dir':
                            dir_input = input("In welche Richtung sollen die Pumpen laufen? (v für vorwärts, r für rückwärts): ")
                            if dir_input.lower() == 'v':
                                pumpen_controller.changeDir(True)
                                print("Pumpen auf vorwärts gesetzt.")
                            elif dir_input.lower() == 'r':
                                pumpen_controller.changeDir(False)
                                print("Pumpen auf rückwärts gesetzt.")
                            else:
                                print("Ungültige Eingabe. Bitte 'v' oder 'r' eingeben.")
                        elif pumpen_command.lower() == 'a':
                            ml_amount = input("Wie viel ml sollen alle Pumpen pumpen? ")
                            try:
                                ml_amount = float(ml_amount)
                                pumpen_controller.all_pump_ml(ml_amount)
                            except ValueError:
                                print("Ungültige Eingabe. Bitte eine Zahl eingeben.")
                        else:
                            try:
                                pump_id = int(pumpen_command)
                                ml_amount = input(f"Wie viel ml soll Pumpe {pump_id} pumpen? ")
                                try:
                                    ml_amount = float(ml_amount)
                                    seconds_per_ml = pumpen_controller.seconds_per_ml[str(pump_id)]
                                    wait_time = seconds_per_ml * ml_amount
                                    print(f"Pumpe {pump_id} pumpt {ml_amount} ml (Dauer: {wait_time:.2f} s)")
                                    pumpen_controller.all_on([pump_id])
                                    time.sleep(wait_time)
                                    pumpen_controller.all_off([pump_id])
                                    print(f"Pumpe {pump_id} fertig.")
                                except ValueError:
                                    print("Ungültige menge. Bitte eine Zahl eingeben.")
                            except ValueError:
                                print("Ungültige Pumpe. Bitte eine Zahl eingeben.")
                    except KeyboardInterrupt:
                        GPIO.cleanup()
                        print("❌ Manuell abgebrochen.")
                        return
            elif command.lower() == 's':
                back_steps = input("Wie viele Schritte zurückfahren? ")
                try:
                    back_steps = int(back_steps)
                    steps -= back_steps
                    element.AXIS._do_step(back_steps, False)
                    axis_steps[current] -= back_steps
                except ValueError:
                    print("Ungültige Eingabe. Bitte eine Zahl eingeben.")
        
        except KeyboardInterrupt:
            GPIO.cleanup()
            print("❌ Manuell abgebrochen.")
            break
        


GPIO.cleanup()

print("GPIO cleaned up.")


    
    

GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
with open('config.json', 'r') as f:
    config = json.load(f)

#-----------------------------
# Hubtisch initialisieren
#-----------------------------

hub_end_stop_pin = config['gpio']['endstops']['hub']
hub_step_pin = config['gpio']["stepper_motors"]['hub']['step_pin']
hub_en_pin = config['gpio']["stepper_motors"]['hub']['en_pin']
hub_dir_pin = config['gpio']["stepper_motors"]['hub']['dir_pin']
hub_axis = motorcontroller.Axis(
    name="Hubtisch-Achse",
    pin_step=hub_step_pin,
    pin_dir=hub_dir_pin,
    pin_en=hub_en_pin,
    run_delay=config['axes']['step_delay_hub'],
    endstop_pins=[hub_end_stop_pin]
)
hub_tisch = HubTisch.HubTisch(
    AXIS=hub_axis,
    endstop_pin=hub_end_stop_pin
)

#-----------------------------
# Linearführung initialisieren
#-----------------------------
lin_end_stop_pin_vorne = config['gpio']['endstops']['linear_vorne']
lin_end_stop_pin_hinten = config['gpio']['endstops']['linear_hinten']
lin_axis = motorcontroller.Axis(
    name="Linear-Achse",
    pin_step=config['gpio']["stepper_motors"]['linear']['step_pin'],
    pin_dir=config['gpio']["stepper_motors"]['linear']['dir_pin'],
    pin_en=config['gpio']["stepper_motors"]['linear']['en_pin'],
    run_delay=config['axes']['step_delay_lin'],
    endstop_pins=[lin_end_stop_pin_vorne, lin_end_stop_pin_hinten]
)
linear_fuehrung = LinearFuehrung.LinearFuehrung(
    axis=lin_axis,
    endstop_pin_vorne=lin_end_stop_pin_vorne,
    endstop_pin_hinten=lin_end_stop_pin_hinten
)

#-----------------------------
# Spritzkopf initialisieren
#-----------------------------
syr_end_stop_pin_links = config['gpio']['endstops']['syringe_links']
syr_end_stop_pin_rechts = config['gpio']['endstops']['syringe_rechts']

syr_axis = motorcontroller.Axis(
    name="Spritzkopf-Achse",
    pin_step=config['gpio']["stepper_motors"]['syringe']['step_pin'],
    pin_dir=config['gpio']["stepper_motors"]['syringe']['dir_pin'],
    pin_en=config['gpio']["stepper_motors"]['syringe']['en_pin'],
    run_delay=config['axes']['step_delay_syr'],
    endstop_pins=[syr_end_stop_pin_links, syr_end_stop_pin_rechts]
)
syr_max_volume_ml = config["positions"]['syringe']['max_volume_ml']
syr_steps_per_ml = config["positions"]['syringe']['steps_per_ml']

spritzkopf = Spritzkopf.SyringeHead(
    axis=syr_axis,
    steps_per_ml=syr_steps_per_ml,
    max_volume_ml=syr_steps_per_ml,
    draw_towards_positive=True,
    start_volume_ml=0.0,
    endstop_pin_links=syr_end_stop_pin_links,
    endstop_pin_rechts=syr_end_stop_pin_rechts
)
#-----------------------------
# Pumpen initialisieren
#-----------------------------
# pumpen initialisieren
pump1= config["gpio"]["relais"]["relais1"]
pump2= config["gpio"]["relais"]["relais2"]
pump3= config["gpio"]["relais"]["relais3"]
pump4= config["gpio"]["relais"]["relais4"]
pump5= config["gpio"]["relais"]["relais5"]
relais6= config["gpio"]["relais"]["relais6"]
relais7= config["gpio"]["relais"]["relais7"]
relais8= config["gpio"]["relais"]["relais8"]
pumpen_controller = pumpenSteuerung.__init__(pump1, pump2, pump3, pump4, pump5, relais6, relais7, relais8)


command = input("Welches Element soll vermessen werden? (hub/lin/syr): ")
if command.lower() == 'hub':
    measure_positions(hub_tisch)
elif command.lower() == 'lin':
    measure_positions(linear_fuehrung)
elif command.lower() == 'syr':
    measure_positions(spritzkopf)



