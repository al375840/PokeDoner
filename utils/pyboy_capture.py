from pyboy import PyBoy
from pyboy.utils import WindowEvent
from PIL import Image

def iniciar_emulador(rom_path: str) -> PyBoy:
    pyboy = PyBoy(rom_path, window="SDL2", debug=False)
    pyboy.set_emulation_speed(1) 
    return pyboy


def capturar_pantalla(pyboy: PyBoy) -> Image.Image:
    screen = pyboy.botsupport_manager().screen()
    return screen.screen_image().convert("RGB")

def simular_input(pyboy: PyBoy, decision: str):
    tecla = None
    d = decision.lower()

    if "press a" in d or "a" == d:
        tecla = WindowEvent.PRESS_BUTTON_A
    elif "press b" in d or "b" == d:
        tecla = WindowEvent.PRESS_BUTTON_B
    elif "move up" in d or "up" == d:
        tecla = WindowEvent.PRESS_ARROW_UP
    elif "move down" in d or "down" == d:
        tecla = WindowEvent.PRESS_ARROW_DOWN
    elif "move left" in d or "left" == d:
        tecla = WindowEvent.PRESS_ARROW_LEFT
    elif "move right" in d or "right" == d:
        tecla = WindowEvent.PRESS_ARROW_RIGHT
    elif "start" in d:
        tecla = WindowEvent.PRESS_BUTTON_START
    elif "select" in d:
        tecla = WindowEvent.PRESS_BUTTON_SELECT

    if tecla:
        print(f"Simulando entrada: {tecla}")
        pyboy.send_input(tecla)

