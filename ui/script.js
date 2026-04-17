// Connecting to Local Backend with Hindsight
const API_URL = "http://localhost:5000/api/chat";

const chatBox = document.getElementById('chat-box');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');

let messageHistory = [
    { role: "system", content: "You are the Shadow Floor Engineer an expert AI assistant that monitors sensors and helps with factory operations." }
];

function addMessage(content, isUser = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${isUser ? 'user' : 'system'}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = isUser ? 'U' : '⚡';
    
    const textContainer = document.createElement('div');
    textContainer.className = 'message-content';
    textContainer.textContent = content; // using textContent to prevent XSS
    
    // Add elements in correct order
    if (isUser) {
        msgDiv.appendChild(textContainer);
        msgDiv.appendChild(avatar);
    } else {
        msgDiv.appendChild(avatar);
        msgDiv.appendChild(textContainer);
    }
    
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showTypingIndicator() {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message system typing';
    msgDiv.id = 'typing-indicator-msg';
    
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = '⚡';
    
    const textContainer = document.createElement('div');
    textContainer.className = 'message-content typing-indicator';
    textContainer.innerHTML = '<span></span><span></span><span></span>';
    
    msgDiv.appendChild(avatar);
    msgDiv.appendChild(textContainer);
    
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator-msg');
    if (indicator) indicator.remove();
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = userInput.value.trim();
    if (!text) return;

    // Add user message to UI and history
    addMessage(text, true);
    messageHistory.push({ role: "user", content: text });
    userInput.value = '';

    // Show typing
    showTypingIndicator();

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                messages: messageHistory
            })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.error || 'Server Error');
        }

        const data = await response.json();
        const aiResponse = data.response;

        removeTypingIndicator();
        addMessage(aiResponse, false);
        messageHistory.push({ role: "assistant", content: aiResponse });

    } catch (error) {
        removeTypingIndicator();
        addMessage(`Error connecting to Groq: ${error.message}`, false);
    }
});
