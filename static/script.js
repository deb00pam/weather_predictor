document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const messagesContainer = document.getElementById('messages');
    const sendText = document.querySelector('.send-text');
    const loadingText = document.querySelector('.loading-text');

    // Focus on input when page loads
    userInput.focus();

    chatForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const message = userInput.value.trim();
        if (!message) return;

        // Add user message to chat
        addMessage(message, 'user');
        
        // Clear input and disable form
        userInput.value = '';
        setLoading(true);
        
        // Show typing indicator
        const typingIndicator = showTypingIndicator();
        
        try {
            // Send message to backend
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });

            // Remove typing indicator
            removeTypingIndicator(typingIndicator);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                // Add bot response to chat
                addMessage(data.response, 'bot');
            } else {
                // Add error message
                addErrorMessage(data.error || 'Sorry, I encountered an error processing your request.');
            }
            
        } catch (error) {
            console.error('Error:', error);
            removeTypingIndicator(typingIndicator);
            addErrorMessage('Sorry, I\'m having trouble connecting to the weather services. Please try again.');
        } finally {
            setLoading(false);
            userInput.focus();
        }
    });

    function addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        if (sender === 'user') {
            messageContent.textContent = content;
        } else {
            // For bot messages, we want to preserve formatting
            messageContent.innerHTML = formatBotMessage(content);
        }
        
        messageDiv.appendChild(messageContent);
        messagesContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function addErrorMessage(content) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message bot-message';
        
        const errorContent = document.createElement('div');
        errorContent.className = 'message-content error-message';
        errorContent.innerHTML = `<strong>Error:</strong> ${content}`;
        
        errorDiv.appendChild(errorContent);
        messagesContainer.appendChild(errorDiv);
        
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function formatBotMessage(content) {
        // Convert markdown-like formatting to HTML
        let formatted = content
            // Bold text with **
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Convert line breaks to <br>
            .replace(/\n\n/g, '<br><br>')
            .replace(/\n/g, '<br>')
            // Convert bullet points
            .replace(/^- (.*$)/gim, '• $1')
            // Convert numbered lists
            .replace(/^(\d+)\. (.*$)/gim, '$1. $2');
        
        return formatted;
    }

    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.innerHTML = `
            <strong style="color: #667eea;">Weather Bot:</strong> 
            <span style="margin-left: 10px;">Analyzing weather data</span>
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        return typingDiv;
    }

    function removeTypingIndicator(indicator) {
        if (indicator && indicator.parentNode) {
            indicator.parentNode.removeChild(indicator);
        }
    }

    function setLoading(isLoading) {
        sendButton.disabled = isLoading;
        userInput.disabled = isLoading;
        
        if (isLoading) {
            sendText.style.display = 'none';
            loadingText.style.display = 'inline-flex';
        } else {
            sendText.style.display = 'inline';
            loadingText.style.display = 'none';
        }
    }

    // Handle Enter key in input
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    // Auto-resize input on mobile
    if (window.innerWidth <= 768) {
        userInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    }
});