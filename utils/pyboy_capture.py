# utils/pyboy_capture.py
import os
from pyboy import PyBoy
from PIL import Image
import logging
from typing import Optional # <-- ¡NUEVA IMPORTACIÓN NECESARIA!

# NO configures logging.basicConfig aquí si ya lo haces en main.py
# Si main.py no lo hiciera, puedes descomentar la línea de abajo:
# logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

DEFAULT_SAVE_STATE_FILENAME = "pokemon_blue.state"

def iniciar_emulador(rom_path: str, save_state_file: str = DEFAULT_SAVE_STATE_FILENAME) -> PyBoy:
    pyboy_instance = None
    loaded_successfully = False

    if os.path.exists(save_state_file):
        try:
            with open(save_state_file, "rb") as f:
                # Pasa loaded_state=f al constructor de PyBoy para cargar el estado
                pyboy_instance = PyBoy(rom_path, window="SDL2", debug=False, loaded_state=f)
            print(f"Partida cargada desde: {save_state_file}")
            loaded_successfully = True
        except Exception as e:
            logging.error(f"Error al cargar el estado desde '{save_state_file}': {e}. Iniciando nueva partida.")
    
    if not loaded_successfully:
        pyboy_instance = PyBoy(rom_path, window="SDL2", debug=False)
        if not os.path.exists(save_state_file):
            print(f"No se encontró archivo de guardado en '{save_state_file}'. Iniciando nueva partida.")
        else:
            print(f"Iniciando nueva partida debido a fallo al cargar estado existente.")
    
    if pyboy_instance:
        pyboy_instance.set_emulation_speed(1) # Velocidad normal
    else:
        raise RuntimeError(f"No se pudo inicializar PyBoy con el ROM: {rom_path}")
        
    return pyboy_instance

def guardar_partida(pyboy_instance: PyBoy, save_state_file: str = DEFAULT_SAVE_STATE_FILENAME):
    if not pyboy_instance:
        print("Error al guardar: instancia de PyBoy no válida.")
        return
    try:
        save_dir = os.path.dirname(save_state_file)
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir)
            print(f"Directorio de guardado creado: {save_dir}")
            
        with open(save_state_file, "wb") as f:
            pyboy_instance.save_state(f)
        print(f"Partida guardada en: {save_state_file}")
    except Exception as e:
        print(f"Error al guardar la partida en '{save_state_file}': {e}")

def capturar_pantalla(pyboy_instance: PyBoy) -> Image.Image:
    """
    Captura la pantalla del emulador PyBoy y la devuelve como una imagen PIL.
    """
    try:
        # PYBOY 2.x: pyboy_instance.screen_image() es el método directo para obtener PIL Image.
        screen_image = pyboy_instance.screen_image() 
        return screen_image
    except AttributeError:
        # Fallback si screen_image() no existe, usa .screen y accede a su atributo .image
        screen_data_object = pyboy_instance.screen
        screen_image = screen_data_object.image # ¡SIN paréntesis, ya es el objeto Image!
        return screen_image
    except Exception as e:
        logging.error(f"Error inesperado al capturar pantalla: {e}")
        raise

# Esta función mapea la decisión de texto a la cadena de PyBoy (ej. 'left', 'a', 'start')
# para usar con pyboy.button(string).
def mapear_decision_a_pyboy_key(decision: str) -> Optional[str]: # <-- ¡CORRECCIÓN AQUÍ!
    decision_norm = decision.strip().upper()

    key_map = {
        'A': 'a',
        'B': 'b',
        'START': 'start',
        'SELECT': 'select',
        'UP': 'up',
        'DOWN': 'down', 
        'LEFT': 'left',
        'RIGHT': 'right',
        'NONE': None, # Para indicar que no se debe presionar nada
        # Añade aquí otras variaciones que tu modelo Gemini pueda generar
        'PRESS A': 'a',
        'PRESS B': 'b',
        'GO UP': 'up',
        'GO DOWN': 'down', 
        'GO LEFT': 'left',
        'GO RIGHT': 'right',
        'MOVE UP': 'up',
        'MOVE DOWN': 'down',
        'MOVE LEFT': 'left',
        'MOVE RIGHT': 'right',
        
    }
    
    return key_map.get(decision_norm)