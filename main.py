# main.py
import time
import os
import threading # Importado directamente
import traceback # Para imprimir tracebacks completos en errores

from utils.gemini_agent import GeminiAgent
from utils.pyboy_capture import (
    iniciar_emulador, 
    capturar_pantalla, 
    simular_input, 
    guardar_partida, 
    DEFAULT_SAVE_STATE_FILENAME
)
from utils.memory_buffer import MemoriaContexto

ROM_PATH = "game/pokemon_blue.gb" 

SAVES_DIR = "saves"
if not os.path.exists(SAVES_DIR):
    try:
        os.makedirs(SAVES_DIR)
        print(f"Directorio de guardado '{SAVES_DIR}' creado.")
    except OSError as e:
        print(f"ADVERTENCIA: No se pudo crear el directorio '{SAVES_DIR}'. Se usará el directorio actual. Error: {e}")
        SAVE_STATE_FILE_PATH = DEFAULT_SAVE_STATE_FILENAME
    else:
        SAVE_STATE_FILE_PATH = os.path.join(SAVES_DIR, DEFAULT_SAVE_STATE_FILENAME)
else:
    SAVE_STATE_FILE_PATH = os.path.join(SAVES_DIR, DEFAULT_SAVE_STATE_FILENAME)

INTERVALO_TICKS_DECISION = 300
INTERVALO_TICKS_GUARDADO_PERIODICO = 18000

pyboy = None
agente = None
memoria = None

decision_actual_global = None
esperando_respuesta_global = False
imagen_para_hilo_global = None
contexto_para_hilo_global = None
# --- Fin Variables Globales ---

def consulta_gemini_thread():
    global decision_actual_global, esperando_respuesta_global, imagen_para_hilo_global, contexto_para_hilo_global, agente

    if agente is None or imagen_para_hilo_global is None or contexto_para_hilo_global is None:
        print("[ERROR HILO] Agente o datos de entrada no listos para el hilo.")
        decision_actual_global = "[ERROR] Datos no listos para IA"
        esperando_respuesta_global = False
        return

    try:
        start_time = time.time()
        # Usa las variables globales que preparamos con los datos actuales
        decision_raw = agente.decidir(imagen_para_hilo_global, contexto_para_hilo_global)
        end_time = time.time()
        print(f"Gemini respondió en {end_time - start_time:.2f} segundos con: '{decision_raw}'")
        decision_actual_global = decision_raw
    except Exception as e_consulta:
        print(f"[ERROR en Hilo Consulta Gemini] {e_consulta}")
        traceback.print_exc() # Imprime el traceback del error en el hilo
        decision_actual_global = "[ERROR] Falla en consulta de agente"
    finally:
        esperando_respuesta_global = False # Marcar como no esperando, incluso si hay error


def main_loop():
    global pyboy, agente, memoria # Para inicializarlas aquí
    global decision_actual_global, esperando_respuesta_global, imagen_para_hilo_global, contexto_para_hilo_global

    try:
        print(f"Intentando iniciar emulador con ROM: '{ROM_PATH}' y archivo de guardado: '{SAVE_STATE_FILE_PATH}'")
        pyboy = iniciar_emulador(ROM_PATH, save_state_file=SAVE_STATE_FILE_PATH)
        agente = GeminiAgent() # Asegúrate que tu GOOGLE_API_KEY está configurada
        memoria = MemoriaContexto(max_turnos=10) # Guardar más turnos puede dar mejor contexto
        print("--- Componentes inicializados ---")
    except Exception as e_init:
        print(f"FALLO CRÍTICO DURANTE LA INICIALIZACIÓN: {e_init}")
        traceback.print_exc()
        return 

    tick_count = 0
    last_save_tick = 0 
    
    print("Emulador iniciado. Bucle principal comenzando...")
    try:
        while True:
            if not pyboy.tick(): 
                print("La emulación de PyBoy se ha detenido. Saliendo del bucle.")
                break
            
            tick_count += 1

            if tick_count % INTERVALO_TICKS_DECISION == 0 and not esperando_respuesta_global:
                imagen_para_hilo_global = capturar_pantalla(pyboy)
                contexto_para_hilo_global = memoria.obtener()
                esperando_respuesta_global = True 
                print(f"Tick {tick_count}: Captura realizada, solicitando decisión a Gemini...")
                
                thread = threading.Thread(target=consulta_gemini_thread, daemon=True)
                thread.start()

            if decision_actual_global is not None:
                print(f"Tick {tick_count}: Aplicando decisión '{decision_actual_global}'")
                simular_input(pyboy, decision_actual_global)
                memoria.actualizar(f"Tick {tick_count}: Yo (IA) decidí '{decision_actual_global}'")
                decision_actual_global = None

            # Guardado periódico
            if INTERVALO_TICKS_GUARDADO_PERIODICO > 0 and (tick_count - last_save_tick >= INTERVALO_TICKS_GUARDADO_PERIODICO):
                print(f"Tick {tick_count}: Guardando partida periódicamente...")
                guardar_partida(pyboy, save_state_file=SAVE_STATE_FILE_PATH)
                last_save_tick = tick_count
            
            time.sleep(0.005) 

    except KeyboardInterrupt:
        print("\nInterrupción por teclado detectada.")
    except Exception as e_loop:
        print(f"\nHa ocurrido un error inesperado en el bucle principal: {e_loop}")
        traceback.print_exc()
    finally:
        if pyboy:
            print("Guardando partida final antes de salir...")
            guardar_partida(pyboy, save_state_file=SAVE_STATE_FILE_PATH)
            print("Deteniendo PyBoy...")
            pyboy.stop() 
            print("PyBoy detenido. ¡Adiós!")
        else:
            print("PyBoy no fue inicializado o ya fue detenido. Saliendo.")

if __name__ == '__main__':
    main_loop()