# main.py
import time
import os
import threading
import traceback
import logging

from utils.gemini_agent import GeminiAgent
from utils.pyboy_capture import (
    iniciar_emulador, 
    capturar_pantalla, 
    mapear_decision_a_pyboy_key, # Importamos la función de mapeo
    guardar_partida, 
    DEFAULT_SAVE_STATE_FILENAME
)
from utils.memory_buffer import MemoriaContexto

# --- Configuración de Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# --- Fin Configuración de Logging ---

ROM_PATH = "game/pokemon_blue.gb" 

SAVES_DIR = "saves"
if not os.path.exists(SAVES_DIR):
    try:
        os.makedirs(SAVES_DIR)
        logging.info(f"Directorio de guardado '{SAVES_DIR}' creado.")
    except OSError as e:
        logging.warning(f"ADVERTENCIA: No se pudo crear el directorio '{SAVES_DIR}'. Se usará el directorio actual. Error: {e}")
        SAVE_STATE_FILE_PATH = os.path.join(SAVES_DIR, DEFAULT_SAVE_STATE_FILENAME)
else:
    SAVE_STATE_FILE_PATH = os.path.join(SAVES_DIR, DEFAULT_SAVE_STATE_FILENAME)

# Intervalo de ticks para que la IA tome una decisión
INTERVALO_TICKS_DECISION = 300 
# Intervalo de ticks para guardar la partida periódicamente
INTERVALO_TICKS_GUARDADO_PERIODICO = 18000

pyboy = None
agente = None
memoria = None

decision_actual_global = None
esperando_respuesta_global = False
imagen_para_hilo_global = None
contexto_para_hilo_global = None

# --- Variables Globales para Control de Teclas (Simplificadas para pyboy.button(string)) ---
# No necesitamos rastrear el estado de las teclas aquí, ya que pyboy.button() hace un toque.
# Si el movimiento no es suficiente, ajustaremos la lógica de pulsación más tarde.
# --- Fin Variables Globales ---


def consulta_gemini_thread():
    global decision_actual_global, esperando_respuesta_global, imagen_para_hilo_global, contexto_para_hilo_global, agente

    if agente is None or imagen_para_hilo_global is None or contexto_para_hilo_global is None:
        logging.error("[ERROR HILO] Agente o datos de entrada no listos para el hilo.")
        decision_actual_global = "[ERROR] Datos no listos para IA"
        esperando_respuesta_global = False
        return

    try:
        start_time = time.time()
        decision_raw = agente.decidir(imagen_para_hilo_global, contexto_para_hilo_global)
        end_time = time.time()
        logging.info(f"Gemini respondió en {end_time - start_time:.2f} segundos con: '{decision_raw}'")
        decision_actual_global = decision_raw
    except Exception as e_consulta:
        logging.error(f"[ERROR en Hilo Consulta Gemini] {e_consulta}")
        traceback.print_exc()
        decision_actual_global = "[ERROR] Falla en consulta de agente"
    finally:
        esperando_respuesta_global = False


def main_loop():
    global pyboy, agente, memoria
    global decision_actual_global, esperando_respuesta_global, imagen_para_hilo_global, contexto_para_hilo_global
    # Ya no necesitamos variables globales de control de teclas complejas aquí

    try:
        logging.info(f"Intentando iniciar emulador con ROM: '{ROM_PATH}' y archivo de guardado: '{SAVE_STATE_FILE_PATH}'")
        pyboy = iniciar_emulador(ROM_PATH, save_state_file=SAVE_STATE_FILE_PATH)
        agente = GeminiAgent()
        memoria = MemoriaContexto(max_turnos=10)
        logging.info("--- Componentes inicializados ---")
    except Exception as e_init:
        logging.critical(f"FALLO CRÍTICO DURANTE LA INICIALIZACIÓN: {e_init}")
        traceback.print_exc()
        return 

    tick_count = 0
    last_save_tick = 0 
    
    logging.info("Emulador iniciado. Bucle principal comenzando...")
    try:
        while True:
            if not pyboy.tick(): 
                logging.info("La emulación de PyBoy se ha detenido. Saliendo del bucle.")
                break
            
            tick_count += 1

            # Lógica para solicitar decisión a Gemini
            # Simplificado: ya no hay lógica de "mantener tecla" aquí
            if tick_count % INTERVALO_TICKS_DECISION == 0 and not esperando_respuesta_global:
                imagen_para_hilo_global = capturar_pantalla(pyboy)
                contexto_para_hilo_global = memoria.obtener()
                esperando_respuesta_global = True 
                logging.info(f"Tick {tick_count}: Captura realizada, solicitando decisión a Gemini...")
                
                thread = threading.Thread(target=consulta_gemini_thread, daemon=True)
                thread.start()

            # Lógica para aplicar la decisión de Gemini
            if decision_actual_global is not None:
                logging.info(f"Tick {tick_count}: Procesando decisión '{decision_actual_global}'")
                
                # Mapear la decisión de texto a la cadena de PyBoy (ej. 'left', 'a')
                pyboy_key_string = mapear_decision_a_pyboy_key(decision_actual_global) 
                
                # Si se obtuvo una cadena de tecla válida, simular el toque
                if pyboy_key_string:
                    logging.info(f"Simulando toque de botón: '{pyboy_key_string}' (para la decisión: '{decision_actual_global}')")
                    pyboy.button(pyboy_key_string) # <-- Uso directo de pyboy.button(string)
                else:
                    logging.info(f"Decisión '{decision_actual_global}' no mapeada o es 'NONE'. No se simula entrada.")
                
                memoria.actualizar(f"Tick {tick_count}: Yo (IA) decidí '{decision_actual_global}'")
                decision_actual_global = None # Limpiar la decisión actual

            # Guardado periódico
            if INTERVALO_TICKS_GUARDADO_PERIODICO > 0 and (tick_count - last_save_tick >= INTERVALO_TICKS_GUARDADO_PERIODICO):
                logging.info(f"Tick {tick_count}: Guardando partida periódicamente...")
                guardar_partida(pyboy, save_state_file=SAVE_STATE_FILE_PATH)
                last_save_tick = tick_count
            
            time.sleep(0.005) # Pequeña pausa para evitar usar el 100% de la CPU

    except KeyboardInterrupt:
        logging.info("\nInterrupción por teclado detectada.")
    except Exception as e_loop:
        logging.error(f"\nHa ocurrido un error inesperado en el bucle principal: {e_loop}")
        traceback.print_exc()
    finally:
        # Aquí no necesitamos liberar teclas explícitamente porque pyboy.button() hace un toque.
        # Si hubiéramos usado button_press/release de forma manual, necesitaríamos liberarlas aquí.
        if pyboy:
            logging.info("Guardando partida final antes de salir...")
            guardar_partida(pyboy, save_state_file=SAVE_STATE_FILE_PATH)
            logging.info("Deteniendo PyBoy...")
            pyboy.stop() 
            logging.info("PyBoy detenido. ¡Adiós!")
        else:
            logging.info("PyBoy no fue inicializado o ya fue detenido. Saliendo.")

if __name__ == '__main__':
    main_loop()