from flask import Flask, render_template
from .config import Config
from . import api
import os

# Hardware backend dynamisch laden
from .hw import mock_impl, rpi_impl  # noqa: F401

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # API Blueprint
    app.register_blueprint(api.bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5001)))
