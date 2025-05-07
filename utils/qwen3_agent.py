from openai import OpenAI
from PIL import Image
from openrouter_config import OPENROUTER_API_KEY
import base64
import io

class QwenAgent:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY
        )

    def decidir(self, imagen: Image.Image, contexto: str) -> str:
        # Convertir imagen a base64
        buffered = io.BytesIO()
        imagen.save(buffered, format="PNG")
        image_base64 = "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode("utf-8")

        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant playing Pokémon Blue. Only reply with one of: Press A, Press B, Move UP, Move DOWN, Move LEFT, Move RIGHT, Open MENU, Close MENU."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": image_base64
                    },
                    {
                        "type": "text",
                        "text": f"You are playing Pokémon Blue. This is the current screen.\nRecent history:\n{contexto}\nWhat should the player do next?"
                    }
                ]
            }
        ]

from openai import OpenAI
from PIL import Image
from openrouter_config import OPENROUTER_API_KEY
import base64
import io

class QwenAgent:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY
        )

    def decidir(self, imagen: Image.Image, contexto: str) -> str:
        # Convertir imagen a base64
        buffered = io.BytesIO()
        imagen.save(buffered, format="PNG")
        image_base64 = "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode("utf-8")

        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant playing Pokémon Blue. Only reply with one of: Press A, Press B, Move UP, Move DOWN, Move LEFT, Move RIGHT, Open MENU, Close MENU."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": image_base64
                    },
                    {
                        "type": "text",
                        "text": f"You are playing Pokémon Blue. This is the current screen.\nRecent history:\n{contexto}\nWhat should the player do next?"
                    }
                ]
            }
        ]

        try:
            completion = self.client.chat.completions.create(
                model="qwen/qwen3-30b-a3b:free",
                messages=messages,
                extra_headers={
                    "HTTP-Referer": "https://pokedoner.ai",
                    "X-Title": "PokeDonerBot"
                }
            )

            if completion and completion.choices:
                respuesta = completion.choices[0].message.content.strip()
            else:
                respuesta = "[ERROR] Empty response from model."

        except Exception as e:
            print(f"[ERROR] Fallo al contactar con OpenRouter: {e}")
            respuesta = "[ERROR] OpenRouter request failed."

        return respuesta


