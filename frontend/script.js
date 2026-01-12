// Your Render backend URL - UPDATE THIS AFTER DEPLOYMENT
const API_BASE_URL = 'https://mindmate-chatbot-tc9l.onrender.com';
let quoteInterval;

const quoteText = document.getElementById('quoteText');
const quoteAuthor = document.getElementById('quoteAuthor');
const chatButton = document.getElementById('chatButton');
const chatWindow = document.getElementById('chatWindow');
const closeChat = document.getElementById('closeChat');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.getElementById('chatMessages');

const fallbackQuotes = [
    { text: "You are stronger than you seem, braver than you believe, and smarter than you think.", author: "A.A. Milne" },
    { text: "Your mental health is a priority. Your happiness is essential.", author: "MindMate" },
    { text: "Healing is not linear. Be patient with your progress.", author: "Unknown" },
    { text: "It's okay not to be okay. What matters is that you don't give up.", author: "Unknown" },
    { text: "Taking care of your mind is as important as taking care of your body.", author: "Unknown" }
];

document.addEventListener('DOMContentLoaded', function() {
    loadQuotes();
    startQuoteRotation();
    setupEventListeners();
});

async function loadQuotes() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/quotes`);
        if (response.ok) {
            const data = await response.json();
            if (data.quotes && data.quotes.length > 0) {
                window.quotes = data.quotes.map(q => ({
                    text: q,
                    author: "MindMate"
                }));
            }
        }
    } catch (error) {
        console.log("Using fallback quotes");
        window.quotes = fallbackQuotes;
    }
}

function startQuoteRotation() {
    if (!window.quotes) window.quotes = fallbackQuotes;
    updateQuote();
    quoteInterval = setInterval(updateQuote, 6000);
}

function updateQuote() {
    if (!window.quotes || window.quotes.length === 0) return;
    
    const randomIndex = Math.floor(Math.random() * window.quotes.length);
    const quote = window.quotes[randomIndex];
    
    quoteText.style.opacity = '0';
    quoteAuthor.style.opacity = '0';
    
    setTimeout(() => {
        quoteText.textContent = quote.text;
        quoteAuthor.textContent = `- ${quote.author}`;
        quoteText.style.opacity = '1';
        quoteAuthor.style.opacity = '1';
    }, 500);
}

function setupEventListeners() {
    chatButton.addEventListener('click', () => {
        chatWindow.classList.add('active');
        chatButton.style.display = 'none';
    });
    
    closeChat.addEventListener('click', () => {
        chatWindow.classList.remove('active');
        chatButton.style.display = 'flex';
    });
    
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    
    document.querySelectorAll('.quick-reply').forEach(button => {
        button.addEventListener('click', (e) => {
            const message = e.target.dataset.message;
            userInput.value = message;
            sendMessage();
        });
    });
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
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        removeTypingIndicator();
        
        const emoji = getEmojiForEmotion(data.emotion);
        addMessage(data.response, 'bot', emoji);
        scrollToBottom();
        
    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator();
        addMessage("I'm having trouble connecting. Please check your internet or try again later.", 'bot');
    }
}

function addMessage(text, sender, emotionEmoji = '') {
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
    
    if (sender === 'bot' && emotionEmoji) {
        const emotionSpan = document.createElement('span');
        emotionSpan.className = 'emotion-tag';
        emotionSpan.textContent = ` ${emotionEmoji}`;
        emotionSpan.style.cssText = 'margin-left: 10px; font-size: 0.9em;';
        contentDiv.appendChild(emotionSpan);
    }
    
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
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
