import time
from utils.qwen3_agent import QwenAgent
from utils.pyboy_capture import iniciar_emulador, capturar_pantalla, simular_input
from utils.memory_buffer import MemoriaContexto

pyboy = iniciar_emulador("game/pokemon_blue.gb")
agente = QwenAgent()
memoria = MemoriaContexto()

tick_count = 0
intervalo_ticks = 30  # cada 30 frames (~0.5s a 60fps)

imagen = None
decision = None
esperando_respuesta = False

while True:
    pyboy.tick()
    tick_count += 1

    if tick_count % intervalo_ticks == 0 and not esperando_respuesta:
        imagen = capturar_pantalla(pyboy)
        contexto = memoria.obtener()
        esperando_respuesta = True

        # Lanzamos la decisión en un hilo separado (para no bloquear el loop)
        import threading
        def consulta():
            global decision, esperando_respuesta
            decision = agente.decidir(imagen, contexto)
            esperando_respuesta = False
        threading.Thread(target=consulta).start()

    # Si ya hay una decisión disponible, la usamos
    if decision:
        print(f"Decisión recibida: {decision}")
        simular_input(pyboy, decision)
        memoria.actualizar(f"Decisión: {decision}")
        decision = None  # reinicia

    time.sleep(0.01)  # reduce CPU (ajustable)
