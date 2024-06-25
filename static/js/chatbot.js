// Function to open the chatbot modal
function openChatbot() {
    document.getElementById('chatbotModal').classList.remove('hidden');
}

// Function to close the chatbot modal
function closeChatbot() {
    document.getElementById('chatbotModal').classList.add('hidden');
}

// Function to handle sending messages
function sendMessage() {
    const userInput = document.getElementById('userInput').value;
    if (userInput.trim() !== '') {
        addMessageToChat('User', userInput);
        fetchChatbotResponse(userInput);
        document.getElementById('userInput').value = '';  // Clear input
    }
}

// Function to handle the 'Enter' key press
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

// Function to add messages to the chat window
function addMessageToChat(sender, message) {
    const chatWindow = document.getElementById('chatWindow');
    const messageElement = document.createElement('div');
    messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
    chatWindow.appendChild(messageElement);
    chatWindow.scrollTop = chatWindow.scrollHeight;  // Scroll to the bottom
}

// Function to fetch chatbot response from the server
function fetchChatbotResponse(userQuery) {
    fetch('/chatbot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: userQuery })
    })
    .then(response => response.json())
    .then(data => {
        addMessageToChat('WeatherBot', data.response);
    })
    .catch(error => {
        console.error('Error fetching chatbot response:', error);
        addMessageToChat('WeatherBot', 'Sorry, there was an error processing your request.');
    });
}
