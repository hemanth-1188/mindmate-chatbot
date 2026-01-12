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

# SINGLE CORS CONFIG - NO DUPLICATES
CORS(app, supports_credentials=True)

emotion_detector = EmotionDetector()
safety_layer = SafetyLayer()
groq_handler = GroqHandler()

quotes = [
    "You are stronger than you seem, braver than you believe, and smarter than you think.",
    "Your mental health is a priority. Your happiness is essential.",
    "Healing is not linear. Be patient with your progress.",
    "It's okay not to be okay. What matters is that you don't give up.",
    "Taking care of your mind is as important as taking care of your body.",
    "Your feelings are valid. Your experiences are real.",
    "One small crack does not mean you are broken.",
    "Mental health is not a destination, but a process.",
    "You don't have to be positive all the time.",
    "The strongest people are those who win battles we know nothing about.",
    "Progress, not perfection.",
    "You are worthy of love and care, especially from yourself.",
    "This too shall pass.",
    "Be gentle with yourself. You're doing the best you can.",
    "Your story isn't over yet."
]

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'response': 'Please share how you\'re feeling.',
                'emotion': 'neutral',
                'is_crisis': False
            })
        
        safety_result = safety_layer.check_safety(user_message)
        if safety_result['is_crisis']:
            return jsonify({
                'response': f"I'm really concerned. Please reach out immediately: {' | '.join(safety_result['resources'])}",
                'emotion': 'crisis',
                'is_crisis': True
            })
        
        emotion = emotion_detector.detect_emotion(user_message)
        response = groq_handler.get_response(user_message, emotion)
        
        return jsonify({
            'response': response,
            'emotion': emotion,
            'is_crisis': False
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            'response': 'I\'m having trouble processing that. Could you try again?',
            'emotion': 'neutral',
            'is_crisis': False
        }), 500

@app.route('/api/quotes', methods=['GET', 'OPTIONS'])
def get_quotes():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({'quotes': quotes})

@app.route('/api/random-quote', methods=['GET', 'OPTIONS'])
def get_random_quote():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({'quote': random.choice(quotes)})

@app.route('/health', methods=['GET', 'OPTIONS'])
def health():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({'status': 'healthy', 'service': 'MindMate API', 'version': '1.0'})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting MindMate API on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)