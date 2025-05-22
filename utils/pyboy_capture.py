# utils/pyboy_capture.py
import os
from pyboy import PyBoy
from pyboy.utils import WindowEvent
from PIL import Image

DEFAULT_SAVE_STATE_FILENAME = "pokemon_blue.state" # Usado si no se especifica otro

def iniciar_emulador(rom_path: str, save_state_file: str = DEFAULT_SAVE_STATE_FILENAME) -> PyBoy:
    pyboy_instance = None
    loaded_successfully = False

    if os.path.exists(save_state_file):
        try:
            with open(save_state_file, "rb") as f:
                # Asegúrate de que PyBoy sepa el nombre del ROM al cargar el estado
                # El primer argumento del constructor PyBoy es siempre el path al ROM.
                pyboy_instance = PyBoy(rom_path, window="SDL2", debug=False, loaded_state=f)
            print(f"Partida cargada desde: {save_state_file}")
            loaded_successfully = True
        except FileNotFoundError: # Específico por si acaso, aunque os.path.exists ya lo cubre
            print(f"Archivo de guardado '{save_state_file}' no encontrado. Iniciando nueva partida.")
        except Exception as e:
            print(f"Error al cargar el estado desde '{save_state_file}': {e}. Iniciando nueva partida.")
    
    if not loaded_successfully:
        # Siempre se necesita el rom_path para inicializar PyBoy, incluso si se carga un estado.
        # Si la carga falló o el archivo no existe, inicializa sin loaded_state.
        pyboy_instance = PyBoy(rom_path, window="SDL2", debug=False)
        if not os.path.exists(save_state_file):
            print(f"No se encontró archivo de guardado en '{save_state_file}'. Iniciando nueva partida.")
        else: # Llegó aquí porque la carga falló pero el archivo existía
             print(f"Iniciando nueva partida debido a fallo al cargar estado existente.")
    
    if pyboy_instance:
        pyboy_instance.set_emulation_speed(1) # Velocidad normal
    else:
        # Esto es crítico y no debería pasar si el ROM es válido y PyBoy está bien instalado
        raise RuntimeError(f"No se pudo inicializar PyBoy con el ROM: {rom_path}")
        
    return pyboy_instance

def guardar_partida(pyboy: PyBoy, save_state_file: str = DEFAULT_SAVE_STATE_FILENAME):
    if not pyboy:
        print("Error al guardar: instancia de PyBoy no válida.")
        return
    try:
        save_dir = os.path.dirname(save_state_file)
        if save_dir and not os.path.exists(save_dir): # Crea el directorio si no existe
            os.makedirs(save_dir)
            print(f"Directorio de guardado creado: {save_dir}")
            
        with open(save_state_file, "wb") as f:
            pyboy.save_state(f) # Guarda el estado del emulador
        print(f"Partida guardada en: {save_state_file}")
    except Exception as e:
        print(f"Error al guardar la partida en '{save_state_file}': {e}")

def capturar_pantalla(pyboy: PyBoy) -> Image.Image:
    if not pyboy:
        raise ValueError("Instancia de PyBoy no válida para capturar pantalla.")
    screen = pyboy.botsupport_manager().screen()
    return screen.screen_image().convert("RGB")

def simular_input(pyboy: PyBoy, decision: str):
    if not pyboy:
        print("Error al simular input: instancia de PyBoy no válida.")
        return
        
    tecla = None
    d = decision.strip().lower() # .strip() para quitar espacios extra

    # Mapeo de decisiones a teclas
    if "press a" == d or "a" == d: # Comparación exacta después de lower() y strip()
        tecla = WindowEvent.PRESS_BUTTON_A
    elif "press b" == d or "b" == d:
        tecla = WindowEvent.PRESS_BUTTON_B
    elif "move up" == d or "up" == d:
        tecla = WindowEvent.PRESS_ARROW_UP
    elif "move down" == d or "down" == d:
        tecla = WindowEvent.PRESS_ARROW_DOWN
    elif "move left" == d or "left" == d:
        tecla = WindowEvent.PRESS_ARROW_LEFT
    elif "move right" == d or "right" == d:
        tecla = WindowEvent.PRESS_ARROW_RIGHT
    elif "open menu" == d or "start" == d: # Mapear "open menu" y "start" a START
        tecla = WindowEvent.PRESS_BUTTON_START
    elif "select" == d:
        tecla = WindowEvent.PRESS_BUTTON_SELECT
    # No hay "close menu" explícito; se asume que la IA usará "Press B" o "Open MENU" (START)
    # según el contexto del juego para cerrar menús.

    if tecla is not None: # Importante: verificar que tecla no sea None
        print(f"Simulando entrada: {tecla} (para la decisión: '{decision}')")
        pyboy.send_input(tecla)
        # Para la mayoría de los juegos, un tick después del input ayuda a procesarlo.
        # Si las acciones no parecen registrarse, descomenta la siguiente línea.
        # pyboy.tick() 
    else:
        print(f"Advertencia: No se mapeó ninguna tecla para la decisión recibida: '{decision}'")