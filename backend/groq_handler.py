import os
import requests
from dotenv import load_dotenv

load_dotenv()

class GroqHandler:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = "llama-3.1-8b-instant"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        
        if self.api_key:
            print(f"✅ Groq API ready | Model: {self.model}")
        else:
            print("⚠️ GROQ_API_KEY not found in environment variables")
        
        self.system_prompt = """You are MindMate, an empathetic mental health companion.
        Provide emotional support tailored to the user's emotion.
        
        GUIDELINES:
        1. Be warm, caring, and validating
        2. Never give medical or professional advice
        3. Ask open-ended questions
        4. Suggest healthy coping strategies
        5. Respond in 1-3 conversational sentences
        6. Vary your responses - don't repeat yourself
        7. If someone mentions serious issues, suggest professional help
        
        NEVER: Diagnose, prescribe, or claim to be a therapist."""
    
    def get_response(self, user_message, emotion=None):
        if not self.api_key:
            return "Hello! I'm MindMate. The server needs to be configured with an API key."
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            messages = [{"role": "system", "content": self.system_prompt}]
            
            if emotion and emotion != 'neutral':
                enhanced_message = f"[User is feeling {emotion}] {user_message}"
                messages.append({"role": "user", "content": enhanced_message})
            else:
                messages.append({"role": "user", "content": user_message})
            
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 200,
                "top_p": 0.9
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ Groq API Error: {response.status_code} - {response.text[:100]}")
                return "I'm having some technical difficulties. Please try again in a moment."
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.Timeout:
            return "I'm taking a bit longer to respond. Please give me a moment."
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
            return "I'm having trouble connecting right now. Please try again later."
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return "I'm here to listen. Could you tell me more about how you're feeling?"