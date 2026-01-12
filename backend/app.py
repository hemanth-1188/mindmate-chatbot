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

# Allow Netlify frontend
CORS(app, origins=[
    "http://localhost:5000",
    "http://localhost:8000",
    "https://mindmate.netlify.app",
    "https://*.netlify.app"
])

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
    "Your story isn't over yet.",
    "Every emotion has its purpose, even the difficult ones.",
    "Your feelings are messengers, not permanent residents.",
    "Healing happens in moments we choose to be kind to ourselves.",
    "The bravest thing you can do is feel your feelings fully.",
    "Progress in mental health is rarely a straight line.",
    "Self-compassion is the foundation of all healing.",
    "Your worth isn't determined by your productivity.",
    "Rest is not a reward - it's a requirement.",
    "Boundaries are an act of self-love.",
    "It's okay to outgrow people who don't grow with you."
]

@app.route('/api/chat', methods=['POST'])
def chat():
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

@app.route('/api/quotes', methods=['GET'])
def get_quotes():
    return jsonify({'quotes': quotes})

@app.route('/api/random-quote', methods=['GET'])
def get_random_quote():
    return jsonify({'quote': random.choice(quotes)})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'MindMate API', 'version': '1.0'})

@app.route('/')
def home():
    return jsonify({
        'message': 'MindMate API is running',
        'endpoints': {
            'chat': '/api/chat (POST)',
            'quotes': '/api/quotes (GET)',
            'health': '/health (GET)'
        },
        'frontend_url': 'https://mindmate.netlify.app'
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting MindMate API on port {port}")
    print(f"🌐 Frontend: https://mindmate.netlify.app")
    print(f"🔗 API Base: http://localhost:{port}")
    app.run(debug=False, host='0.0.0.0', port=port)