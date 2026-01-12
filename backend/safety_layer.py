class SafetyLayer:
    def __init__(self):
        self.crisis_keywords = [
            'suicide', 'kill myself', 'end my life', 'want to die',
            'self harm', 'cut myself', 'harm myself', 'end it all'
        ]
    
    def check_safety(self, message):
        message_lower = message.lower()
        for keyword in self.crisis_keywords:
            if keyword in message_lower:
                return {
                    'is_crisis': True,
                    'resources': [
                        "National Suicide Prevention Lifeline: 988",
                        "Crisis Text Line: Text HOME to 741741",
                        "Emergency Services: 911 or your local emergency number"
                    ]
                }
        return {'is_crisis': False}