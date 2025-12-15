"""
GPIO Kompatibilitätsmodul für cross-platform Entwicklung.
Verwendet echtes RPi.GPIO auf dem Raspberry Pi, sonst einen Mock.
"""

try:
    import RPi.GPIO as GPIO
    print("[INFO] Echtes RPi.GPIO geladen")
except (ImportError, ModuleNotFoundError):
    from . import mock_gpio as GPIO
    print("[INFO] Mock GPIO für Windows/Mac geladen")

__all__ = ['GPIO']
