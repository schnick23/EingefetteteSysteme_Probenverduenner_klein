import sys
from unittest.mock import MagicMock

# Mock RPi.GPIO if not available (e.g. on macOS)
try:
    import RPi.GPIO as GPIO
except ImportError:
    print("⚠️  RPi.GPIO not found. Using Mock for development.")
    
    # Create a mock module for RPi
    MockRPi = MagicMock()
    MockGPIO = MagicMock()
    
    # Set up constants that might be used
    MockGPIO.BCM = "BCM"
    MockGPIO.BOARD = "BOARD"
    MockGPIO.OUT = "OUT"
    MockGPIO.IN = "IN"
    MockGPIO.HIGH = 1
    MockGPIO.LOW = 0
    MockGPIO.PUD_UP = "PUD_UP"
    MockGPIO.PUD_DOWN = "PUD_DOWN"
    MockGPIO.FALLING = "FALLING"
    MockGPIO.RISING = "RISING"
    MockGPIO.BOTH = "BOTH"
    
    # Assign to sys.modules BEFORE any other imports
    sys.modules['RPi'] = MockRPi
    sys.modules['RPi.GPIO'] = MockGPIO
    MockRPi.GPIO = MockGPIO

from flask import Flask, render_template, request

from .config import Config
from . import api
import os
import uuid
from .tasks.runner import runner, TaskState, example_dilute# Hardware backend dynamisch laden
from .hw import mock_impl, rpi_impl  # noqa: F401

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # API Blueprint
    app.register_blueprint(api.bp)

    @app.route("/")
    def index():
        return render_template("index.html")
    
    # @app.route("/check/<task_id>")
    # def check_page(task_id: str):
    #     return render_template("check.html", task_id=task_id)
    
    @app.route("/check", methods=["POST"])
    def check_page():
        import json
        
        # Get the processed data from the hidden input
        processed_data_str = request.form.get("processedData")
        task_id = None
        
        if processed_data_str:
            processed_data = json.loads(processed_data_str)
        else:
            processed_data = {}
        
        start_volume = processed_data.get("stockVolume", request.form.get("stock_Volume"))
        dilution1 = processed_data.get("factors", {}).get("2", request.form.get("factorDilution1"))
        dilution2 = processed_data.get("factors", {}).get("1", request.form.get("factorDilution2"))
        dilution3 = processed_data.get("factors", {}).get("0", request.form.get("factorDilution3"))
        
        info1 = processed_data.get("info1")
        info2 = processed_data.get("info2")
        info3 = processed_data.get("info3")

        return render_template(
            "check.html",
            start_volume=start_volume,
            dilution1=dilution1,
            dilution2=dilution2,
            dilution3=dilution3,
            info1=info1,
            info2=info2,
            info3=info3,
            task_id=task_id,
            processed_json=processed_data_str or "{}"
        )

    @app.route("/running/<task_id>")
    def running(task_id: str):
        return render_template("running.html", task_id=task_id)
    

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5001)))
