from . import HubTisch
from . import LinearFuehrung
from . import Spritzkopf
import time
import json
from . import motorcontroller
from .gpio_compat import GPIO


GPIO.cleanup()
print("GPIO cleaned up.")

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
    pin_en=hub_en_pin
)
hub_tisch = HubTisch.Hubtisch(
    AXIS=hub_axis,
    endstop_pin=end_stop_pin
)
hub_tisch.home()

lin_axis = motorcontroller.Axis(
    name="Linear-Achse",
    pin_step=config['gpio']["stepper_motors"]['linear']['step_pin'],
    pin_dir=config['gpio']["stepper_motors"]['linear']['dir_pin'],
    pin_en=config['gpio']["stepper_motors"]['linear']['en_pin']
)
end_stop_pin_vorne = config['gpio']['endstops']['linear_vorne']
end_stop_pin_hinten = config['gpio']['endstops']['linear_hinten']
linear_fuehrung = LinearFuehrung.LinearFuehrung(
    axis=lin_axis,
    endstop_pin_vorne=end_stop_pin_vorne,
    endstop_pin_hinten=end_stop_pin_hinten
)
linear_fuehrung.home()

syr_axis = motorcontroller.Axis(
    name="Spritzkopf-Achse",
    pin_step=config['gpio']["stepper_motors"]['syringe']['step_pin'],
    pin_dir=config['gpio']["stepper_motors"]['syringe']['dir_pin'],
    pin_en=config['gpio']["stepper_motors"]['syringe']['en_pin']
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

spritzkopf.home()
GPIO.cleanup()
print("GPIO cleaned up.")