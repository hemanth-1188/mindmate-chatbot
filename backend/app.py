from flask import Flask, request, jsonify
from flask_cors import CORS
from emotion_detector import EmotionDetector
from safety_layer import SafetyLayer
from groq_handler import GroqHandler
import random
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Allow all origins for development
CORS(app, origins=['*'])


emotion_detector = EmotionDetector()
safety_layer = SafetyLayer()
groq_handler = GroqHandler()

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        user_language = data.get('language', 'english')
        response_language = data.get('response_language', 'english')
        
        if not user_message:
            return jsonify({
                'response': 'Please share how you\'re feeling.',
                'emotion': 'neutral',
                'is_crisis': False,
                'language': response_language
            })
        
        safety_result = safety_layer.check_safety(user_message)
        if safety_result['is_crisis']:
            return jsonify({
                'response': f"I'm really concerned. Please reach out immediately: {' | '.join(safety_result['resources'])}",
                'emotion': 'crisis',
                'is_crisis': True,
                'language': 'english'  # Always English for crisis
            })
        
        emotion = emotion_detector.detect_emotion(user_message, user_language)
        response = groq_handler.get_response(user_message, emotion, user_language, response_language)
        
        return jsonify({
            'response': response,
            'emotion': emotion,
            'is_crisis': False,
            'language': response_language
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            'response': 'I\'m having trouble processing that. Could you try again?',
            'emotion': 'neutral',
            'is_crisis': False,
            'language': 'english'
        }), 500

@app.route('/api/quotes', methods=['GET'])
def get_quotes():
    quotes = [
        "You are stronger than you seem, braver than you believe, and smarter than you think.",
        "Your mental health is a priority. Your happiness is essential.",
        "Healing is not linear. Be patient with your progress.",
        "It's okay not to be okay. What matters is that you don't give up.",
        "Taking care of your mind is as important as taking care of your body."
    ]
    return jsonify({'quotes': quotes})

@app.route('/api/random-quote', methods=['GET'])
def get_random_quote():
    quotes = [
        "You are stronger than you seem, braver than you believe, and smarter than you think.",
        "Your mental health is a priority. Your happiness is essential.",
        "Healing is not linear. Be patient with your progress.",
        "It's okay not to be okay. What matters is that you don't give up.",
        "Taking care of your mind is as important as taking care of your body."
    ]
    return jsonify({'quote': random.choice(quotes)})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy', 
        'service': 'MindMate API', 
        'version': '2.0',
        'features': ['multilingual', 'voice', 'emotion_detection']
    })

@app.route('/')
def home():
    return jsonify({
        'message': 'MindMate API is running',
        'version': '2.0',
        'endpoints': {
            'chat': '/api/chat (POST)',
            'quotes': '/api/quotes (GET)',
            'health': '/health (GET)'
        },
        'features': {
            'languages': ['english', 'hinglish', 'tanglish'],
            'voice': 'input_output_supported',
            'emotions': '12+ emotions detected'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting MindMate API v2.0 on port {port}")
    print(f"🌐 Features: Multilingual + Voice Support")
    print(f"🔗 API Base: http://localhost:{port}")
    app.run(debug=False, host='0.0.0.0', port=port)
