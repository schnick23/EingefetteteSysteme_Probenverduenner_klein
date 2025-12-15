from . import HubTisch
from . import LinearFuehrung
from . import Spritzkopf
import time
import json
from . import motorcontroller
from .gpio_compat import GPIO
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
            command = input("Drücke 'q' um abzubrechen, 'i' für aktuelle steps, 'w' zum vorwärts fahren, 's' zum zurück fahren: ")
            
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
                print(f"HubTisch Schritte: {hub_steps}, Linear Schritte: {linear_steps}, Spritzkopf Schritte: {syringe_steps}")
                print(f"Current: {current}")
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

end_stop_pin = config['gpio']['endstops']['hub']
hub_step_pin = config['gpio']["stepper_motors"]['hub']['step_pin']
hub_en_pin = config['gpio']["stepper_motors"]['hub']['en_pin']
hub_dir_pin = config['gpio']["stepper_motors"]['hub']['dir_pin']
hub_axis = motorcontroller.Axis(
    name="Hubtisch-Achse",
    pin_step=hub_step_pin,
    pin_dir=hub_dir_pin,
    pin_en=hub_en_pin,
    run_delay=0.0001
)
hub_tisch = HubTisch.Hubtisch(
    AXIS=hub_axis,
    endstop_pin=end_stop_pin
)
lin_axis = motorcontroller.Axis(
    name="Linear-Achse",
    pin_step=config['gpio']["stepper_motors"]['linear']['step_pin'],
    pin_dir=config['gpio']["stepper_motors"]['linear']['dir_pin'],
    pin_en=config['gpio']["stepper_motors"]['linear']['en_pin'],
    run_delay=0.00005
)
end_stop_pin_vorne = config['gpio']['endstops']['linear_vorne']
end_stop_pin_hinten = config['gpio']['endstops']['linear_hinten']
linear_fuehrung = LinearFuehrung.LinearFuehrung(
    axis=lin_axis,
    endstop_pin_vorne=end_stop_pin_vorne,
    endstop_pin_hinten=end_stop_pin_hinten
)

syr_axis = motorcontroller.Axis(
    name="Spritzkopf-Achse",
    pin_step=config['gpio']["stepper_motors"]['syringe']['step_pin'],
    pin_dir=config['gpio']["stepper_motors"]['syringe']['dir_pin'],
    pin_en=config['gpio']["stepper_motors"]['syringe']['en_pin'],
    run_delay=0.0001
)
end_stop_pin_links = config['gpio']['endstops']['syringe_links']
end_stop_pin_rechts = config['gpio']['endstops']['syringe_rechts']
spritzkopf = Spritzkopf.SyringeHead(
    axis=syr_axis,
    steps_per_ml=2000.0,  # Beispielwert, anpassen!
    max_volume_ml=10.0,   # Beispielwert, anpassen!
    draw_towards_positive=True,
    start_volume_ml=0.0,
    endstop_pin_links=end_stop_pin_links,
    endstop_pin_rechts=end_stop_pin_rechts
)
command = input("Welches Element soll vermessen werden? (hub/lin/syr): ")
if command.lower() == 'hub':
    measure_positions(hub_tisch)
elif command.lower() == 'lin':
    measure_positions(linear_fuehrung)
elif command.lower() == 'syr':
    measure_positions(spritzkopf)



