"""
Mock für RPi.GPIO zur Windows-Entwicklung
"""

# GPIO Modes
BCM = 11
BOARD = 10

# Pin Modes
IN = 1
OUT = 0

# Pull-up/Pull-down
PUD_OFF = 20
PUD_DOWN = 21
PUD_UP = 22

# Edge Detection
RISING = 31
FALLING = 32
BOTH = 33

# Pin states
HIGH = 1
LOW = 0

_pin_states = {}
_pin_modes = {}

def setmode(mode):
    """Mock setmode"""
    pass

def setwarnings(flag):
    """Mock setwarnings"""
    pass

def setup(pin, mode, pull_up_down=PUD_OFF, initial=LOW):
    """Mock setup"""
    _pin_modes[pin] = mode
    if mode == OUT:
        _pin_states[pin] = initial

def output(pin, state):
    """Mock output"""
    _pin_states[pin] = state
    print(f"[MOCK GPIO] Pin {pin} -> {state}")

def input(pin):
    """Mock input"""
    return _pin_states.get(pin, LOW)

def cleanup(pin=None):
    """Mock cleanup"""
    if pin is None:
        _pin_states.clear()
        _pin_modes.clear()
    else:
        _pin_states.pop(pin, None)
        _pin_modes.pop(pin, None)

def add_event_detect(pin, edge, callback=None, bouncetime=None):
    """Mock add_event_detect"""
    pass

def remove_event_detect(pin):
    """Mock remove_event_detect"""
    pass

def event_detected(pin):
    """Mock event_detected"""
    return False

class PWM:
    """Mock PWM class"""
    def __init__(self, pin, frequency):
        self.pin = pin
        self.frequency = frequency
        self.duty_cycle = 0
        
    def start(self, duty_cycle):
        """Start PWM"""
        self.duty_cycle = duty_cycle
        print(f"[MOCK PWM] Pin {self.pin} started at {duty_cycle}% duty cycle")
        
    def ChangeDutyCycle(self, duty_cycle):
        """Change duty cycle"""
        self.duty_cycle = duty_cycle
        
    def stop(self):
        """Stop PWM"""
        self.duty_cycle = 0
        print(f"[MOCK PWM] Pin {self.pin} stopped")
