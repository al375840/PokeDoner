import time
import os
import threading
import traceback
import logging

from utils.gemini_agent import GeminiAgent
from utils.pyboy_capture import (
    init_emulator, 
    capture_screen, 
    map_decision_to_pyboy_key, 
    save_game, 
    DEFAULT_SAVE_STATE_FILENAME
)
from utils.memory_buffer import ContextMemory

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ROM_PATH = "game/pokemon_blue.gb" 

SAVES_DIR = "saves"
if not os.path.exists(SAVES_DIR):
    try:
        os.makedirs(SAVES_DIR)
        logging.info(f"Save directory '{SAVES_DIR}' created.")
    except OSError as e:
        logging.warning(f"WARNING: Could not create directory '{SAVES_DIR}'. Current directory will be used. Error: {e}")
        SAVE_STATE_FILE_PATH = DEFAULT_SAVE_STATE_FILENAME
    else:
        SAVE_STATE_FILE_PATH = os.path.join(SAVES_DIR, DEFAULT_SAVE_STATE_FILENAME)
else:
    SAVE_STATE_FILE_PATH = os.path.join(SAVES_DIR, DEFAULT_SAVE_STATE_FILENAME)

DECISION_TICKS_INTERVAL = 300 
PERIODIC_SAVE_TICKS_INTERVAL = 18000

pyboy = None
agent = None
memory = None

current_decision_global = None
waiting_for_response_global = False
image_for_thread_global = None
context_for_thread_global = None

def gemini_query_thread():
    global current_decision_global, waiting_for_response_global, image_for_thread_global, context_for_thread_global, agent

    if agent is None or image_for_thread_global is None or context_for_thread_global is None:
        logging.error("Thread ERROR: Agent or input data not ready.")
        current_decision_global = "ERROR: Data not ready for AI"
        waiting_for_response_global = False
        return

    try:
        start_time = time.time()
        raw_decision = agent.decide(image_for_thread_global, context_for_thread_global)
        end_time = time.time()
        logging.info(f"Gemini responded in {end_time - start_time:.2f} seconds with: '{raw_decision}'")
        current_decision_global = raw_decision
    except Exception as e_query:
        logging.error(f"Error in Gemini Query Thread: {e_query}")
        traceback.print_exc()
        current_decision_global = "ERROR: Agent query failed"
    finally:
        waiting_for_response_global = False


def main_loop():
    global pyboy, agent, memory
    global current_decision_global, waiting_for_response_global, image_for_thread_global, context_for_thread_global

    try:
        logging.info(f"Attempting to start emulator with ROM: '{ROM_PATH}' and save file: '{SAVE_STATE_FILE_PATH}'")
        pyboy = init_emulator(ROM_PATH, save_state_file=SAVE_STATE_FILE_PATH)
        agent = GeminiAgent()
        memory = ContextMemory(max_turns=10)
        logging.info("--- Components initialized ---")
    except Exception as e_init:
        logging.critical(f"CRITICAL FAILURE DURING INITIALIZATION: {e_init}")
        traceback.print_exc()
        return 

    tick_count = 0
    last_save_tick = 0 
    
    logging.info("Emulator started. Main loop beginning...")
    try:
        while True:
            if not pyboy.tick(): 
                logging.info("PyBoy emulation has stopped. Exiting loop.")
                break
            
            tick_count += 1

            if tick_count % DECISION_TICKS_INTERVAL == 0 and not waiting_for_response_global:
                image_for_thread_global = capture_screen(pyboy)
                context_for_thread_global = memory.get_context()
                waiting_for_response_global = True 
                logging.info(f"Tick {tick_count}: Screen captured, requesting decision from Gemini...")
                
                thread = threading.Thread(target=gemini_query_thread, daemon=True)
                thread.start()

            if current_decision_global is not None:
                logging.info(f"Tick {tick_count}: Processing decision '{current_decision_global}'")
                
                pyboy_key_string = map_decision_to_pyboy_key(current_decision_global) 
                
                if pyboy_key_string:
                    logging.info(f"Simulating button tap: '{pyboy_key_string}' (for decision: '{current_decision_global}')")
                    pyboy.button(pyboy_key_string)
                else:
                    logging.info(f"Decision '{current_decision_global}' not mapped or is 'NONE'. No input simulated.")
                
                memory.update(f"Tick {tick_count}: I (AI) decided '{current_decision_global}'")
                current_decision_global = None

            if PERIODIC_SAVE_TICKS_INTERVAL > 0 and (tick_count - last_save_tick >= PERIODIC_SAVE_TICKS_INTERVAL):
                logging.info(f"Tick {tick_count}: Periodically saving game...")
                save_game(pyboy, save_state_file=SAVE_STATE_FILE_PATH)
                last_save_tick = tick_count
            
            time.sleep(0.005)

    except KeyboardInterrupt:
        logging.info("\nKeyboard interruption detected.")
    except Exception as e_loop:
        logging.error(f"\nAn unexpected error occurred in the main loop: {e_loop}")
        traceback.print_exc()
    finally:
        if pyboy:
            logging.info("Saving final game state before exiting...")
            save_game(pyboy, save_state_file=SAVE_STATE_FILE_PATH)
            logging.info("Stopping PyBoy...")
            pyboy.stop() 
            logging.info("PyBoy stopped. Goodbye!")
        else:
            logging.info("PyBoy was not initialized or already stopped. Exiting.")

if __name__ == '__main__':
    main_loop()