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
        
        self.emotion_keywords = {
            'sad': ['sad', 'depressed', 'unhappy', 'miserable', 'lonely', 'cry', 'tears', 'hurt', 'empty'],
            'anxious': ['anxious', 'worried', 'nervous', 'panic', 'scared', 'afraid', 'fear'],
            'angry': ['angry', 'mad', 'furious', 'annoyed', 'hate', 'rage', 'frustrated'],
            'happy': ['happy', 'joy', 'good', 'great', 'excited', 'wonderful', 'amazing'],
            'stressed': ['stress', 'pressure', 'overwhelmed', 'tired', 'exhausted', 'burnout'],
            'lonely': ['lonely', 'alone', 'isolated', 'abandoned'],
            'confused': ['confused', 'uncertain', 'unsure', 'lost'],
            'hopeless': ['hopeless', 'despair', 'helpless', 'defeated'],
            'guilty': ['guilty', 'regret', 'ashamed', 'sorry'],
            'jealous': ['jealous', 'envious', 'insecure'],
            'proud': ['proud', 'accomplished', 'confident'],
            'grateful': ['grateful', 'thankful', 'appreciative']
        }
    
    def detect_emotion(self, text):
        if not text or len(text.strip()) == 0:
            return 'neutral'
        
        text_lower = text.lower()
        emotion_scores = {emotion: 0 for emotion in self.emotion_keywords}
        
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    emotion_scores[emotion] += 2
        
        sentiment = self.sia.polarity_scores(text)
        
        if sentiment['compound'] < -0.3:
            emotion_scores['sad'] += 3
        elif sentiment['compound'] > 0.3:
            emotion_scores['happy'] += 3
        
        max_emotion = max(emotion_scores, key=emotion_scores.get)
        return max_emotion if emotion_scores[max_emotion] > 0 else 'neutral'