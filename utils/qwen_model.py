from transformers import AutoProcessor, AutoModelForVision2Seq
from qwen_vl_utils import process_vision_info
from PIL import Image
import torch

MODEL_ID = "models/qwen2.5-vl-7b-instruct"

class QwenAgent:
    def __init__(self):
        self.processor = AutoProcessor.from_pretrained(MODEL_ID,
        min_pixels=280*280,
        max_pixels=420*420, 
        trust_remote_code=True)
        self.model = AutoModelForVision2Seq.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        self.tokenizer = self.processor.tokenizer

    def decidir(self, imagen: Image.Image, contexto: str) -> str:
        # 1. Estructura tipo conversación oficial
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": imagen},
                    {"type": "text", "text": "tomate"}
                ]
            }
        ]
# f"""You are playing Pokémon Blue. This is the current screen of the game.Recent history: {contexto} What should the player do next? Choose one of the following actions: Press A Press B Move UP Move DOWN Move LEFT Move RIGHT Open MENU Close MENU"""}
        # 2. Aplica plantilla de chat oficial
        text_prompt = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        # 3. Procesa imagen (y video si existiera)
        image_inputs, video_inputs = process_vision_info(messages)

        # 4. Prepara inputs combinados para el modelo
        inputs = self.processor(
            text=[text_prompt],
            images=image_inputs,
            videos=video_inputs,
            return_tensors="pt",
            padding=True
        ).to("cuda")
        # 5. Generación
        generated_ids = self.model.generate(**inputs, max_new_tokens=4)
        torch.cuda.empty_cache()
        respuesta = self.processor.batch_decode(
            generated_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )[0]
        print("Respuesta generada:", respuesta)
        print("Fin de respuesta")
        return respuesta.strip()
