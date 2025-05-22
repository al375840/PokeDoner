# utils/gemini_agent.py
import google.generativeai as genai
from openrouter_config import GOOGLE_API_KEY 
from PIL import Image
import os
import io

genai.configure(api_key=GOOGLE_API_KEY)
# --- Fin Configuración de la API Key ---

class GeminiAgent:
    def __init__(self, model_name="gemini-1.5-flash-latest"):
        try:
            self.model = genai.GenerativeModel(model_name)
            print(f"Agente Gemini inicializado con el modelo: {model_name}")
        except Exception as e:
            print(f"Error al inicializar el modelo Gemini ({model_name}): {e}")
            print("Asegúrate de que tu GOOGLE_API_KEY es válida y tiene permisos para este modelo.")
            raise

    def decidir(self, imagen: Image.Image, contexto: str) -> str:
        if GOOGLE_API_KEY == "TU_GOOGLE_API_KEY_AQUI":
            print("[ERROR AGENTE] La API Key de Gemini no está configurada. Saltando decisión.")
            return "[ERROR] API Key no configurada"

        prompt_texto_completo = (
            "You are an expert assistant playing Pokémon Blue. You are observing the game screen. "
            "Based on the current screen image and the recent history of actions, "
            "decide the single best next action to take. "
            f"Recent history of your actions:\n{contexto}\n\n"
            "Choose ONLY ONE of the following actions. Do not add any other commentary, explanation, or punctuation. "
            "Your entire response should be just one of these exact phrases:\n"
            "- Press A\n"
            "- Press B\n"
            "- Move UP\n"
            "- Move DOWN\n"
            "- Move LEFT\n"
            "- Move RIGHT\n"
            "- Open MENU\n" 
            "- Select"      
        )
        generation_config = genai.types.GenerationConfig(
            candidate_count=1, 
            max_output_tokens=20, 
            temperature=0.7 
        )

        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
        ]

        contenido_prompt = [imagen, prompt_texto_completo]
        respuesta_modelo = "[ERROR] Respuesta no inicializada"

        try:
            response = self.model.generate_content(
                contents=contenido_prompt,
                generation_config=generation_config,
                safety_settings=safety_settings,
                stream=False 
            )

            if response.candidates:
                respuesta_cruda = response.text.strip()
                acciones_permitidas = [
                    "Press A", "Press B", "Move UP", "Move DOWN", 
                    "Move LEFT", "Move RIGHT", "Open MENU", "Select"
                ]
                for accion_valida in acciones_permitidas:
                    if accion_valida.lower() in respuesta_cruda.lower():
                        respuesta_modelo = accion_valida
                        break 
                else: 
                    print(f"[ADVERTENCIA AGENTE] Respuesta de Gemini ('{respuesta_cruda}') no contiene una acción esperada. Usando cruda.")
                    respuesta_modelo = respuesta_cruda 
            else:
                feedback_razon = "No candidates in response."
                if response.prompt_feedback:
                    feedback_razon = f"Prompt feedback: {response.prompt_feedback.block_reason_message or response.prompt_feedback.block_reason}"
                print(f"[ERROR AGENTE] Respuesta vacía o inválida de Gemini. Razón: {feedback_razon}")
                respuesta_modelo = f"[ERROR] Gemini: {feedback_razon}"

        except Exception as e:
            print(f"[ERROR AGENTE] Fallo al contactar o procesar respuesta de Gemini API: {e}")
            # Intentar obtener más información si es un error de la API de Google
            if hasattr(e, 'message'): # Errores de google.api_core.exceptions
                 print(f"[ERROR AGENTE DETALLE] {e.message}")
            respuesta_modelo = "[ERROR] Falla en solicitud a Gemini API"

        return respuesta_modelo