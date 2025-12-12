import HubTisch
import LinearFuehrung
import Spritzkopf
import time
import json
import motorcontroller

with open('/config.json', 'r') as f:
    config = json.load(f)
end_stop_pin = config['gpio']['endstops']['hub']
hub_step_pin = config['gpio']['hub']['step_pin']
hub_en_pin = config['gpio']['hub']['en_pin']
hub_dir_pin = config['motor_pins']['hub']['dir_pin']
hub_axis = motorcontroller.Axis(
    name="Hubtisch-Achse",
    step_pin=hub_step_pin,
    dir_pin=hub_dir_pin,
    pin_en=hub_en_pin
)
hub_tisch = HubTisch.Hubtisch(
    AXIS=hub_axis,
    endstop_pin=end_stop_pin
)
hub_tisch.home_hub()

lin_axis = motorcontroller.Axis(
    name="Linear-Achse",
    step_pin=config['gpio']['linear']['step_pin'],
    dir_pin=config['motor_pins']['linear']['dir_pin'],
    pin_en=config['motor_pins']['linear']['en_pin']
)
end_stop_pin_vorne = config['gpio']['endstops']['linear_vorne']
end_stop_pin_hinten = config['gpio']['endstops']['linear_hinten']
linear_fuehrung = LinearFuehrung.LinearFuehrung(
    axis=lin_axis,
    endstop_pin_vorne=end_stop_pin_vorne,
    endstop_pin_hinten=end_stop_pin_hinten
)
linear_fuehrung.home_linear()

syr_axis = motorcontroller.Axis(
    name="Spritzkopf-Achse",
    step_pin=config['gpio']['syringe']['step_pin'],
    dir_pin=config['motor_pins']['syringe']['dir_pin'],
    pin_en=config['motor_pins']['syringe']['en_pin']
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

spritzkopf.home_syringe()