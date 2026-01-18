// Your Render backend URL
const API_BASE_URL = 'https://mindmate-chatbot-tc9l.onrender.com';
let quoteInterval;
let speechSynthesis = window.speechSynthesis;
let recognition = null;
let isListening = false;
let selectedLanguage = 'english';
let responseLanguage = 'english';

// DOM Elements
const quoteText = document.getElementById('quoteText');
const quoteAuthor = document.getElementById('quoteAuthor');
const chatButton = document.getElementById('chatButton');
const chatWindow = document.getElementById('chatWindow');
const closeChat = document.getElementById('closeChat');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.getElementById('chatMessages');
const voiceInputBtn = document.getElementById('voiceInputBtn');
const voiceStatus = document.getElementById('voiceStatus');
const playLastResponse = document.getElementById('playLastResponse');
const voiceModal = document.getElementById('voiceModal');
const startVoice = document.getElementById('startVoice');
const skipVoice = document.getElementById('skipVoice');
const currentLang = document.getElementById('currentLang');
const langButtons = document.querySelectorAll('.lang-btn');
const langResponseButtons = document.querySelectorAll('.lang-response-btn');

// Language configurations
const languageConfig = {
    english: {
        name: 'English',
        greetings: ['Hello', 'Hi there', 'Hey'],
        placeholder: 'Type or speak your feelings...',
        voiceStatus: 'Click to speak'
    },
    hinglish: {
        name: 'Hinglish',
        greetings: ['Namaste', 'Hello ji', 'Kaise ho?'],
        placeholder: 'Type karo ya bolo... अपनी feelings share karo',
        voiceStatus: 'Bolnे के लिए click karo'
    },
    tanglish: {
        name: 'Tanglish',
        greetings: ['Vanakkam', 'Hello', 'Eppadi irukeenga?'],
        placeholder: 'Type pannunga ya pesunga... ungal feelings share pannunga',
        voiceStatus: 'Pesalam click pannunga'
    }
};

document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    checkVoiceSupport();
    updateLanguageUI();
});

function setupEventListeners() {
    // Chat button
    chatButton.addEventListener('click', () => {
        chatWindow.classList.add('active');
        chatButton.style.display = 'none';
        showVoiceModal();
    });
    
    // Close chat
    closeChat.addEventListener('click', () => {
        chatWindow.classList.remove('active');
        chatButton.style.display = 'flex';
        stopListening();
    });
    
    // Send message
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    
    // Voice input
    voiceInputBtn.addEventListener('click', toggleVoiceInput);
    
    // Play last response
    playLastResponse.addEventListener('click', () => {
        const lastBotMessage = document.querySelector('.message.bot:last-child .message-content p');
        if (lastBotMessage) {
            speakText(lastBotMessage.textContent);
        }
    });
    
    // Voice modal
    startVoice.addEventListener('click', initVoiceRecognition);
    skipVoice.addEventListener('click', () => {
        voiceModal.classList.remove('active');
    });
    
    // Language selection
    langButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            langButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedLanguage = btn.dataset.lang;
            currentLang.textContent = languageConfig[selectedLanguage].name;
            updatePlaceholder();
        });
    });
    
    // Response language
    langResponseButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            langResponseButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            responseLanguage = btn.dataset.lang;
        });
    });
    
    // Quick replies
    document.querySelectorAll('.quick-reply').forEach(button => {
        button.addEventListener('click', (e) => {
            const message = e.target.closest('.quick-reply').dataset.message;
            userInput.value = message;
            sendMessage();
        });
    });
    
    // Voice play buttons in messages
    document.addEventListener('click', (e) => {
        if (e.target.closest('.voice-play')) {
            const btn = e.target.closest('.voice-play');
            const message = btn.dataset.message;
            speakText(message);
        }
    });
}

function checkVoiceSupport() {
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
        voiceInputBtn.style.display = 'none';
        voiceStatus.textContent = 'Voice not supported';
    }
    
    if (!speechSynthesis) {
        document.querySelectorAll('.voice-play, .voice-play-btn').forEach(el => {
            el.style.display = 'none';
        });
    }
}

function showVoiceModal() {
    if (!localStorage.getItem('voiceSkipped') && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
        setTimeout(() => {
            voiceModal.classList.add('active');
        }, 1000);
    }
}

function initVoiceRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = getSpeechLang();
    
    recognition.onstart = () => {
        isListening = true;
        voiceInputBtn.classList.add('listening');
        voiceStatus.textContent = 'Listening...';
    };
    
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        userInput.value = transcript;
        isListening = false;
        voiceInputBtn.classList.remove('listening');
        voiceStatus.textContent = languageConfig[selectedLanguage].voiceStatus;
        
        // Auto-send if message is long enough
        if (transcript.length > 3) {
            setTimeout(() => sendMessage(), 500);
        }
    };
    
    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        isListening = false;
        voiceInputBtn.classList.remove('listening');
        voiceStatus.textContent = 'Error: ' + event.error;
        setTimeout(() => {
            voiceStatus.textContent = languageConfig[selectedLanguage].voiceStatus;
        }, 2000);
    };
    
    recognition.onend = () => {
        isListening = false;
        voiceInputBtn.classList.remove('listening');
        voiceStatus.textContent = languageConfig[selectedLanguage].voiceStatus;
    };
    
    voiceModal.classList.remove('active');
    localStorage.setItem('voiceSkipped', 'true');
}

function toggleVoiceInput() {
    if (!recognition) {
        initVoiceRecognition();
    }
    
    if (isListening) {
        stopListening();
    } else {
        startListening();
    }
}

function startListening() {
    if (recognition) {
        recognition.start();
    }
}

function stopListening() {
    if (recognition && isListening) {
        recognition.stop();
        isListening = false;
        voiceInputBtn.classList.remove('listening');
        voiceStatus.textContent = languageConfig[selectedLanguage].voiceStatus;
    }
}

function getSpeechLang() {
    switch(selectedLanguage) {
        case 'hinglish': return 'hi-IN';
        case 'tanglish': return 'ta-IN';
        default: return 'en-US';
    }
}

function updateLanguageUI() {
    currentLang.textContent = languageConfig[selectedLanguage].name;
    updatePlaceholder();
}

function updatePlaceholder() {
    userInput.placeholder = languageConfig[selectedLanguage].placeholder;
    voiceStatus.textContent = languageConfig[selectedLanguage].voiceStatus;
}

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;
    
    userInput.value = '';
    addMessage(message, 'user');
    showTypingIndicator();
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                language: selectedLanguage,
                response_language: responseLanguage
            })
        });
        
        const data = await response.json();
        removeTypingIndicator();
        
        addMessage(data.response, 'bot', data.emotion, true);
        scrollToBottom();
        
        // Auto-speak response if voice is enabled
        if (localStorage.getItem('voiceEnabled') === 'true') {
            setTimeout(() => speakText(data.response), 500);
        }
        
    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator();
        addMessage("I'm having trouble connecting. Please check your internet or try again later.", 'bot');
    }
}

function addMessage(text, sender, emotion = '', hasVoice = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'avatar';
    avatarDiv.innerHTML = sender === 'bot' ? 
        '<i class="fas fa-robot"></i>' : 
        '<i class="fas fa-user"></i>';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const textP = document.createElement('p');
    textP.textContent = text;
    contentDiv.appendChild(textP);
    
    if (sender === 'bot') {
        // Add emotion emoji
        if (emotion) {
            const emoji = getEmojiForEmotion(emotion);
            const emotionSpan = document.createElement('span');
            emotionSpan.className = 'emotion-tag';
            emotionSpan.textContent = ` ${emoji}`;
            emotionSpan.style.cssText = 'margin-left: 10px; font-size: 0.9em;';
            contentDiv.appendChild(emotionSpan);
        }
        
        // Add voice play button
        if (hasVoice && speechSynthesis) {
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'message-actions';
            
            const voiceBtn = document.createElement('button');
            voiceBtn.className = 'action-btn voice-play';
            voiceBtn.dataset.message = text;
            voiceBtn.innerHTML = '<i class="fas fa-volume-up"></i> Listen';
            
            actionsDiv.appendChild(voiceBtn);
            contentDiv.appendChild(actionsDiv);
        }
    }
    
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function speakText(text) {
    if (!speechSynthesis) return;
    
    // Stop any ongoing speech
    speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Set language based on response
    switch(responseLanguage) {
        case 'hinglish':
            utterance.lang = 'hi-IN';
            utterance.rate = 0.9;
            break;
        case 'tanglish':
            utterance.lang = 'ta-IN';
            utterance.rate = 0.9;
            break;
        default:
            utterance.lang = 'en-US';
            utterance.rate = 1.0;
    }
    
    utterance.volume = 1;
    utterance.pitch = 1;
    
    speechSynthesis.speak(utterance);
}

function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typingIndicator';
    typingDiv.className = 'message bot';
    typingDiv.innerHTML = `
        <div class="avatar"><i class="fas fa-robot"></i></div>
        <div class="message-content">
            <div class="typing">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    
    const style = document.createElement('style');
    style.textContent = `
        .typing { display: flex; gap: 5px; padding: 10px; }
        .typing span {
            width: 8px; height: 8px; background: #4caf50; border-radius: 50%;
            animation: typing 1.4s infinite ease-in-out;
        }
        .typing span:nth-child(1) { animation-delay: 0s; }
        .typing span:nth-child(2) { animation-delay: 0.2s; }
        .typing span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typing {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
    `;
    document.head.appendChild(style);
    
    chatMessages.appendChild(typingDiv);
    scrollToBottom();
}

function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) typingIndicator.remove();
}

function getEmojiForEmotion(emotion) {
    const emojiMap = {
        'sad': '😔', 'anxious': '😰', 'angry': '😠', 'happy': '😊',
        'stressed': '😫', 'lonely': '😟', 'confused': '😕',
        'hopeless': '😞', 'guilty': '😔', 'jealous': '😒',
        'proud': '😌', 'grateful': '🙏', 'neutral': '💭',
        'crisis': '🚨'
    };
    return emojiMap[emotion] || '💭';
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}