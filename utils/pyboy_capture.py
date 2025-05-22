
import os
from pyboy import PyBoy # Solo importa PyBoy directamente
from PIL import Image
import logging
from typing import Optional # Importación necesaria para Optional[str]


DEFAULT_SAVE_STATE_FILENAME = "pokemon_blue.state"

def iniciar_emulador(rom_path: str, save_state_file: str = DEFAULT_SAVE_STATE_FILENAME) -> PyBoy:
    pyboy_instance = None
    loaded_successfully = False

    pyboy_instance = PyBoy(rom_path, window="SDL2", debug=False)
    
    if pyboy_instance:
        if os.path.exists(save_state_file):
            try:
                with open(save_state_file, "rb") as f:
                    pyboy_instance.load_state(f) # <-- ¡CORRECCIÓN CLAVE AQUÍ! Usar el método load_state
                print(f"Partida cargada desde: {save_state_file}")
                loaded_successfully = True
            except Exception as e:
                logging.error(f"Error al cargar el estado desde '{save_state_file}': {e}. Iniciando nueva partida.")
        else:
            print(f"No se encontró archivo de guardado en '{save_state_file}'. Iniciando nueva partida.")
        
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
    try:
        screen_image = pyboy_instance.screen_image() 
        return screen_image
    except AttributeError:
        screen_data_object = pyboy_instance.screen
        screen_image = screen_data_object.image 
        return screen_image
    except Exception as e:
        logging.error(f"Error inesperado al capturar pantalla: {e}")
        raise

def mapear_decision_a_pyboy_key(decision: str) -> Optional[str]:
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
        'NONE': None, 
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