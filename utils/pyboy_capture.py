import os
from pyboy import PyBoy
from PIL import Image
import logging
from typing import Optional

DEFAULT_SAVE_STATE_FILENAME = "pokemon_blue.state"

def init_emulator(rom_path: str, save_state_file: str = DEFAULT_SAVE_STATE_FILENAME) -> PyBoy:
    pyboy_instance = None
    loaded_successfully = False

    pyboy_instance = PyBoy(rom_path, window="SDL2", debug=False)
    
    if pyboy_instance:
        if os.path.exists(save_state_file):
            try:
                with open(save_state_file, "rb") as f:
                    pyboy_instance.load_state(f)
                print(f"Game loaded from: {save_state_file}")
                loaded_successfully = True
            except Exception as e:
                logging.error(f"Error loading state from '{save_state_file}': {e}. Starting new game.")
        else:
            print(f"No save file found at '{save_state_file}'. Starting new game.")
        
        pyboy_instance.set_emulation_speed(1)
    else:
        raise RuntimeError(f"Could not initialize PyBoy with ROM: {rom_path}")
        
    return pyboy_instance

def save_game(pyboy_instance: PyBoy, save_state_file: str = DEFAULT_SAVE_STATE_FILENAME):
    if not pyboy_instance:
        print("Save error: Invalid PyBoy instance.")
        return
    try:
        save_dir = os.path.dirname(save_state_file)
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir)
            print(f"Save directory created: {save_dir}")
            
        with open(save_state_file, "wb") as f:
            pyboy_instance.save_state(f)
        print(f"Game saved to: {save_state_file}")
    except Exception as e:
        print(f"Error saving game to '{save_state_file}': {e}")

def capture_screen(pyboy_instance: PyBoy) -> Image.Image:
    try:
        screen_image = pyboy_instance.screen_image() 
        return screen_image
    except AttributeError:
        screen_data_object = pyboy_instance.screen
        screen_image = screen_data_object.image 
        return screen_image
    except Exception as e:
        logging.error(f"Unexpected error capturing screen: {e}")
        raise

def map_decision_to_pyboy_key(decision: str) -> Optional[str]:
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