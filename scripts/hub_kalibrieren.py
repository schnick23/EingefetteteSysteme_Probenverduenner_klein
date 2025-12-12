import HubTisch
import time
import json
import motorcontroller

with open('scripts/config.json', 'r') as f:
    config = json.load(f)
end_stop_pin = config['gpio']['endstops']['hub']
hub_axis = motorcontroller.Axis(
    name="Hubtisch-Achse",
    step_pin=config['gpio']['hub']['step_pin'],
    dir_pin=config['motor_pins']['hub']['dir_pin'],
    pin_en=config['motor_pins']['hub']['en_pin']
)
hub_tisch = HubTisch.Hubtisch(
    AXIS=hub_axis,
    endstop_pin=end_stop_pin
)
hub_tisch.home_hub()