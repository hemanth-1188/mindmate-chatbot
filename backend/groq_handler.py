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
            print(f"🌐 Multilingual: Hinglish, Tanglish, English")
        else:
            print("⚠️ GROQ_API_KEY not found in environment variables")
        
        # Language-specific prompts
        self.language_prompts = {
            'english': """You are MindMate, an empathetic mental health companion.
            Respond in English only. Be warm, caring, and validating.
            Provide emotional support tailored to the user's emotion.
            Respond in 1-3 conversational sentences.""",
            
            'hinglish': """You are MindMate, ek empathetic mental health companion.
            Respond in Hinglish (Hindi+English mix). Example: "Aap kaise feel kar rahe ho?"
            Be warm, caring, and validating. Use simple language.
            Provide emotional support tailored to user's emotion.
            Respond in 1-3 conversational sentences.""",
            
            'tanglish': """You are MindMate, oru empathetic mental health companion.
            Respond in Tanglish (Tamil+English mix). Example: "Nee eppadi feel panre?"
            Be warm, caring, and validating. Use simple language.
            Provide emotional support tailored to user's emotion.
            Respond in 1-3 conversational sentences."""
        }
    
    def get_response(self, user_message, emotion=None, user_language='english', response_language='english'):
        if not self.api_key:
            return "Hello! I'm MindMate. The server needs to be configured with an API key."
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Get appropriate system prompt
            system_prompt = self.language_prompts.get(response_language, self.language_prompts['english'])
            
            # Add emotion context
            if emotion and emotion != 'neutral':
                system_prompt += f"\n\nUser is feeling {emotion}. Respond appropriately."
            
            # Add language detection note
            if user_language != 'english':
                system_prompt += f"\n\nNote: User is speaking in {user_language}. Understand their mixed language."
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 250,
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