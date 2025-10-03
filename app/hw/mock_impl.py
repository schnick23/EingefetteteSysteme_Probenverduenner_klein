from .controller import MockHardware, HardwareInterface

def get_hardware() -> HardwareInterface:
    hw = MockHardware()
    hw.initialize()
    return hw
