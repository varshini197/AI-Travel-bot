// history.js
document.addEventListener('DOMContentLoaded', function() {
    // Fetch and display chat history
    const chatHistory = JSON.parse(localStorage.getItem('chatHistory')) || [];
    const historyContainer = document.getElementById('chat-history');

    if (chatHistory.length === 0) {
        historyContainer.innerHTML = '<p>No previous chats available.</p>';
    } else {
        chatHistory.forEach((chat, index) => {
            const chatDiv = document.createElement('div');
            chatDiv.classList.add('chat-entry');
            chatDiv.innerHTML = `
                <h3>Chat ${index + 1}</h3>
                <p><strong>User:</strong> ${chat.user}</p>
                <p><strong>Bot:</strong> ${chat.bot}</p>
            `;
            historyContainer.appendChild(chatDiv);
        });
    }
});
