import google.generativeai as genai
import os
from PIL import Image
import io

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") 

genai.configure(api_key=GOOGLE_API_KEY)

class GeminiAgent:
    def __init__(self, model_name="gemini-1.5-flash-latest"):
        try:
            self.model = genai.GenerativeModel(model_name)
            print(f"Gemini Agent initialized with model: {model_name}")
        except Exception as e:
            print(f"Error initializing Gemini model ({model_name}): {e}")
            print("Ensure your GOOGLE_API_KEY is valid and has permissions for this model.")
            raise

    def decide(self, image: Image.Image, context: str) -> str:
        if GOOGLE_API_KEY is None or GOOGLE_API_KEY == "YOUR_GOOGLE_API_KEY_HERE":
            print("Gemini API Key is not configured. Skipping decision.")
            return "ERROR: API Key not configured"

        full_prompt_text = (
            "You are an expert assistant playing Pokémon Blue. You are observing the game screen. "
            "Based on the current screen image and the recent history of actions, "
            "decide the single best next action to take. "
            f"Recent history of your actions:\n{context}\n\n"
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

        prompt_content = [image, full_prompt_text]
        model_response = "ERROR: Response not initialized"

        try:
            response = self.model.generate_content(
                contents=prompt_content,
                generation_config=generation_config,
                safety_settings=safety_settings,
                stream=False 
            )

            if response.candidates:
                raw_response = response.text.strip()
                allowed_actions = [
                    "Press A", "Press B", "Move UP", "Move DOWN", 
                    "Move LEFT", "Move RIGHT", "Open MENU", "Select"
                ]
                for valid_action in allowed_actions:
                    if valid_action.lower() in raw_response.lower():
                        model_response = valid_action
                        break 
                else: 
                    print(f"AGENT WARNING: Gemini response ('{raw_response}') does not contain an expected action. Using raw response.")
                    model_response = raw_response 
            else:
                feedback_reason = "No candidates in response."
                if response.prompt_feedback:
                    feedback_reason = f"Prompt feedback: {response.prompt_feedback.block_reason_message or response.prompt_feedback.block_reason}"
                print(f"AGENT ERROR: Empty or invalid response from Gemini. Reason: {feedback_reason}")
                model_response = f"ERROR: Gemini: {feedback_reason}"

        except Exception as e:
            print(f"AGENT ERROR: Failed to contact or process Gemini API response: {e}")
            if hasattr(e, 'message'): 
                 print(f"AGENT ERROR DETAILS: {e.message}")
            model_response = "ERROR: Gemini API request failed"

        return model_response