// Internal Messaging JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Auto-refresh unread count
    updateUnreadCount();
    setInterval(updateUnreadCount, 30000); // Update every 30 seconds
    
    // Auto-refresh conversation if on conversation detail page
    if (window.location.pathname.includes('/conversation/')) {
        setInterval(refreshConversation, 10000); // Refresh every 10 seconds
    }
    
    // Message form enhancements
    const messageForm = document.getElementById('message-form');
    if (messageForm) {
        const messageContent = document.getElementById('message-content');
        if (messageContent) {
            // Auto-resize textarea
            messageContent.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = this.scrollHeight + 'px';
            });
            
            // Send message on Ctrl+Enter
            messageContent.addEventListener('keydown', function(e) {
                if (e.ctrlKey && e.key === 'Enter') {
                    e.preventDefault();
                    messageForm.submit();
                }
            });
        }
    }
    
    // Mark messages as read when scrolled to bottom
    const messagesContainer = document.querySelector('.card-body');
    if (messagesContainer) {
        messagesContainer.addEventListener('scroll', function() {
            if (this.scrollTop + this.clientHeight >= this.scrollHeight - 10) {
                markMessagesAsRead();
            }
        });
    }
});

function updateUnreadCount() {
    fetch('/messaging/unread-count/')
        .then(response => response.json())
        .then(data => {
            const unreadCount = data.unread_count;
            const messagesLink = document.querySelector('a[href*="messages"]');
            if (messagesLink) {
                // Remove existing badge
                const existingBadge = messagesLink.querySelector('.badge');
                if (existingBadge) {
                    existingBadge.remove();
                }
                
                // Add new badge if there are unread messages
                if (unreadCount > 0) {
                    const badge = document.createElement('span');
                    badge.className = 'badge bg-danger ms-1';
                    badge.textContent = unreadCount;
                    messagesLink.appendChild(badge);
                }
            }
        })
        .catch(error => console.log('Error updating unread count:', error));
}

function refreshConversation() {
    // Only refresh if user is at the bottom of the conversation
    const messagesContainer = document.querySelector('.card-body');
    if (messagesContainer) {
        const isAtBottom = messagesContainer.scrollTop + messagesContainer.clientHeight >= messagesContainer.scrollHeight - 10;
        
        if (isAtBottom) {
            // Reload the page to get new messages
            window.location.reload();
        }
    }
}

function markMessagesAsRead() {
    // This would typically make an AJAX call to mark messages as read
    // For now, we'll just log that messages should be marked as read
    console.log('Messages should be marked as read');
}

// Utility function to format timestamps
function formatTimestamp(timestamp) {
    const now = new Date();
    const messageTime = new Date(timestamp);
    const diffInSeconds = Math.floor((now - messageTime) / 1000);
    
    if (diffInSeconds < 60) {
        return 'Just now';
    } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
    } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
    } else {
        const days = Math.floor(diffInSeconds / 86400);
        return `${days} day${days !== 1 ? 's' : ''} ago`;
    }
}

// Function to show typing indicator (for future enhancement)
function showTypingIndicator(userId) {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.style.display = 'block';
        typingIndicator.textContent = 'Someone is typing...';
    }
}

// Function to hide typing indicator
function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.style.display = 'none';
    }
}
