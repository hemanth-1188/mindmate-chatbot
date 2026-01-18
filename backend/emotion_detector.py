import re
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

class EmotionDetector:
    def __init__(self):
        try:
            nltk.data.find('vader_lexicon')
        except:
            nltk.download('vader_lexicon', quiet=True)
        
        self.sia = SentimentIntensityAnalyzer()
        
        # Multilingual emotion keywords
        self.emotion_keywords = {
            'sad': {
                'english': ['sad', 'depressed', 'unhappy', 'miserable', 'lonely', 'cry', 'tears', 'hurt', 'empty'],
                'hinglish': ['udass', 'dukhi', 'tanha', 'rona', 'dard', 'ख़ुशी नहीं', 'अकेला'],
                'tanglish': ['sokam', 'kashtam', 'thunbam', 'kalangida', 'துக்கம்', 'கவலை']
            },
            'anxious': {
                'english': ['anxious', 'worried', 'nervous', 'panic', 'scared', 'afraid', 'fear'],
                'hinglish': ['chinta', 'ghabrahat', 'tension', 'डर', 'घबराहट'],
                'tanglish': ['avaludan', 'payama', 'bayama', 'பயம்', 'கவலை']
            },
            'happy': {
                'english': ['happy', 'joy', 'good', 'great', 'excited', 'wonderful', 'amazing'],
                'hinglish': ['khush', 'maza', 'awesome', 'बढ़िया', 'खुश'],
                'tanglish': ['sandhosham', 'nandraga', 'சந்தோஷம்', 'மகிழ்ச்சி']
            },
            'stressed': {
                'english': ['stress', 'pressure', 'overwhelmed', 'tired', 'exhausted', 'burnout'],
                'hinglish': ['tension', 'pressure', 'thakaan', 'थकान', 'तनाव'],
                'tanglish': ['stress', 'pressure', 'thakarnthu', 'அழுத்தம்', 'சோர்வு']
            },
            'angry': {
                'english': ['angry', 'mad', 'furious', 'annoyed', 'hate', 'rage', 'frustrated'],
                'hinglish': ['gussa', 'naraz', 'krodh', 'गुस्सा', 'क्रोध'],
                'tanglish': ['kopa', 'ariyamai', 'கோபம்', 'சினம்']
            }
        }
    
    def detect_emotion(self, text, language='english'):
        if not text or len(text.strip()) == 0:
            return 'neutral'
        
        text_lower = text.lower()
        emotion_scores = {emotion: 0 for emotion in self.emotion_keywords.keys()}
        
        # Check for keywords in all languages
        for emotion, lang_dict in self.emotion_keywords.items():
            # Check current language
            if language in lang_dict:
                for keyword in lang_dict[language]:
                    if keyword.lower() in text_lower:
                        emotion_scores[emotion] += 3
            
            # Also check English as fallback
            if 'english' in lang_dict and language != 'english':
                for keyword in lang_dict['english']:
                    if keyword in text_lower:
                        emotion_scores[emotion] += 2
        
        # Get sentiment score
        sentiment = self.sia.polarity_scores(text)
        
        # Adjust scores based on sentiment
        if sentiment['compound'] < -0.3:
            emotion_scores['sad'] += 3
        elif sentiment['compound'] > 0.3:
            emotion_scores['happy'] += 3
        
        # Find max emotion
        max_emotion = max(emotion_scores, key=emotion_scores.get)
        
        # Only return emotion if score > 2, otherwise neutral
        return max_emotion if emotion_scores[max_emotion] > 2 else 'neutral'