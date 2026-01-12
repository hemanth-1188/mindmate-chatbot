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

# CORS Configuration - ALLOW ALL ORIGINS for testing
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],  # Allow all origins
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": False,
        "max_age": 3600
    },
    r"/health": {
        "origins": ["*"],
        "methods": ["GET", "OPTIONS"]
    },
    r"/": {
        "origins": ["*"],
        "methods": ["GET", "OPTIONS"]
    }
})

# Alternative: Specific origins (use this for production)
# CORS(app, origins=[
#     "http://localhost:5000",
#     "http://localhost:8000",
#     "http://127.0.0.1:5500",  # VS Code Live Server
#     "http://127.0.0.1:3000",
#     "https://mindmate-chatbot-tc9l.onrender.com",
#     "https://*.netlify.app",
#     "https://*.vercel.app",
#     "https://*.onrender.com",
#     "http://localhost",  # Add all possible local URLs
#     "http://127.0.0.1",
#     "http://0.0.0.0",
# ])

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

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response, 200
    
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'response': 'Please share how you\'re feeling.',
                'emotion': 'neutral',
                'is_crisis': False
            }), 200
        
        safety_result = safety_layer.check_safety(user_message)
        if safety_result['is_crisis']:
            return jsonify({
                'response': f"I'm really concerned. Please reach out immediately: {' | '.join(safety_result['resources'])}",
                'emotion': 'crisis',
                'is_crisis': True
            }), 200
        
        emotion = emotion_detector.detect_emotion(user_message)
        response = groq_handler.get_response(user_message, emotion)
        
        return jsonify({
            'response': response,
            'emotion': emotion,
            'is_crisis': False
        }), 200
        
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
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
    return jsonify({'quotes': quotes})

@app.route('/api/random-quote', methods=['GET', 'OPTIONS'])
def get_random_quote():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
    return jsonify({'quote': random.choice(quotes)})

@app.route('/health', methods=['GET', 'OPTIONS'])
def health():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
    return jsonify({'status': 'healthy', 'service': 'MindMate API', 'version': '1.0'})

@app.route('/', methods=['GET', 'OPTIONS'])
def home():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
    return jsonify({
        'message': 'MindMate API is running',
        'endpoints': {
            'chat': '/api/chat (POST)',
            'quotes': '/api/quotes (GET)',
            'health': '/health (GET)'
        },
        'frontend_url': 'https://mindmate.netlify.app'
    })

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting MindMate API on port {port}")
    print(f"🌐 CORS enabled for all origins")
    print(f"🔗 API Base: http://localhost:{port}")
    app.run(debug=False, host='0.0.0.0', port=port)