import os

class Config:
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change")
    HW_BACKEND = os.getenv("HW_BACKEND", "mock")  # 'mock' oder 'rpi'
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data.db")

class TestConfig(Config):
    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"
