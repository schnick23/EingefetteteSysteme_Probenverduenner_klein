from flask import Flask, render_template
from .config import Config
from . import api
import os# Hardware backend dynamisch laden
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
        start_volume = request.form.get("stock_Volume")

        targetV3 = request.form.get("fillDilution3")
        targetV2 = request.form.get("fillDilution2")
        targetV1 = request.form.get("fillDilution1")
        if targetV3 is not None:
            target_volume = targetV3
        elif targetV2 is not None:
            target_volume = targetV2
        elif targetV1 is not None:
            target_volume = targetV1
        
        dilution1   = request.form.get("factorDilution1")
        dilution2   = request.form.get("factorDilution2")
        dilution3   = request.form.get("factorDilution3")

        return render_template(
            "check.html",
            start_volume=start_volume,
            target_volume=target_volume,
            dilution1=dilution1,
            dilution2=dilution2,
            dilution3=dilution3
        )

    @app.route("/running/<task_id>")
    def running(task_id: str):
        return render_template("running.html", task_id=task_id)
    

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5001)))
