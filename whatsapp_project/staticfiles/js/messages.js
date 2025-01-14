// Helper functions
function formatDate(timestamp) {
    const date = new Date(timestamp);
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    };
    return new Intl.DateTimeFormat('en-US', options).format(date);
}

function formatName(nameWithComma) {
    var parts = nameWithComma.split(', ')
    return parts[1] + " " + parts[0]
}

$(document).ready(function () {
    let currentMessageId = null;
    const UPDATE_INTERVAL = 5000;

    function fetchAndUpdateThreads() {
        $.ajax({
            url: '/api/messages/latest/',
            method: 'GET',
            success: function(response) {
                if (response && response.threads) {
                    // Update all thread previews
                    response.threads.forEach(threadData => {
                        const thread = threadData.messages;
                        if (thread && thread.length > 0) {
                            updateMessagePreview(threadData.thread_id, thread);
                            
                            // If this is the currently open thread, update it too
                            if (threadData.thread_id === currentMessageId) {
                                displayMessageThread(thread);
                            }
                        }
                    });
                }
            }
        });
    }

    function updateMessagePreview(messageId, thread) {
        if (!thread || thread.length === 0) return;

        const current_user = $('.userdetails').text().trim();
        const latestMessage = thread[thread.length - 1];
        const messageSnippet = latestMessage.content.substring(0, 50) + 
                             (latestMessage.content.length > 50 ? "..." : "");
        const timestamp = formatDate(latestMessage.timestamp);
        
        const firstMessage = thread[0];
        const originalSender = formatName(firstMessage.sender_name);
        const originalRecipient = formatName(firstMessage.recipient_name);
        
        let nameToShow = current_user === originalSender ? originalRecipient : originalSender;

        let previewElement = $(`.message-preview[data-message-id="${messageId}"]`);
        if (previewElement.length === 0) {
            const newMessageHtml = `
                <div class="message-preview" data-message-id="${messageId}">
                    <div class="sender-info">
                        <span class="sender-name"></span>
                        <span class="message-time"></span>
                    </div>
                    <div class="message-snippet"></div>
                </div>
            `;
            $('#messagesList').append(newMessageHtml);
            previewElement = $(`.message-preview[data-message-id="${messageId}"]`);
        }

        previewElement.find('.sender-info .sender-name').text(nameToShow);
        previewElement.find('.message-snippet').text(messageSnippet);
        previewElement.find('.sender-info .message-time').text(timestamp);
        previewElement.attr('data-timestamp', new Date(latestMessage.timestamp).getTime());
        
        sortMessagePreviews();
    }

    function sortMessagePreviews() {
        const messagesList = $('#messagesList');
        const previews = messagesList.children('.message-preview').get();
        
        previews.sort((a, b) => {
            const timeA = parseInt($(a).attr('data-timestamp'));
            const timeB = parseInt($(b).attr('data-timestamp'));
            return timeB - timeA; // Sort descending (newest first)
        });
        
        $.each(previews, function(idx, preview) {
            messagesList.append(preview);
        });
    }

    function displayMessageThread(thread) {
        const messageThread = $('#messageThread');
        messageThread.empty();
        if (thread && thread.length > 0) {
            thread.forEach(message => {
                messageThread.append(`
                    <div class="message-item ${message.is_sender ? 'sent' : 'received'}">
                        <div class="header">
                            <span class="sender-name">${formatName(message.sender_name)}</span>
                            <span class="message-time">${formatDate(message.timestamp)}</span>
                        </div>
                        <div class="content">
                            ${message.content}
                        </div>
                    </div>
                `);
            });
            scrollToBottom();
        } else {
            messageThread.append('<div class="no-message-selected">No messages to display</div>');
        }
    }

    function scrollToBottom() {
        const messagesContainer = $('#messageThread');
        if (messagesContainer.length) {
            messagesContainer.scrollTop(messagesContainer[0].scrollHeight);
        }
    }

    // Initialize and start periodic updates
    fetchAndUpdateThreads();
    setInterval(fetchAndUpdateThreads, UPDATE_INTERVAL);

    // Event Handlers
    $(document).on('click', '.message-preview', function () {
        const messageId = $(this).data('message-id');
        currentMessageId = messageId;

        $('.message-preview').removeClass('selected');
        $(this).addClass('selected');
        $('#replySection').show();

        // Find the thread data in the latest response
        $.ajax({
            url: '/api/messages/latest/',
            method: 'GET',
            success: function(response) {
                const threadData = response.threads.find(t => t.thread_id === messageId);
                if (threadData && threadData.messages) {
                    displayMessageThread(threadData.messages);
                }
            }
        });
    });

    $('#newMessageBtn').click(function () {
        window.location.href = '/new_message/';
    });

    $('#replyBtn').click(function () {
        if (currentMessageId) {
            window.location.href = `/new_message/?reply_to=${currentMessageId}`;
        }
    });

    $('#logoutBtn').click(function () {
        $.ajax({
            url: '/logout/',
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function () {
                window.location.href = 'http://127.0.0.1:8000/login/';
            },
            error: function (xhr) {
                console.error('Error logging out:', xhr);
            }
        });
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});

// Time-based greeting
document.addEventListener("DOMContentLoaded", function () {
    const now = new Date();
    const hours = now.getHours();
    let greeting = "";

    if (hours < 12 && hours > 4) {
        greeting = "Good Morning\n☀️ ";
    } else if (hours >= 12 && hours < 17) {
        greeting = "Good Afternoon\n🌤️ ";
    } else if (hours >= 15 && hours < 21) {
        greeting = "Good Evening\n🌙 ";
    } else {
        greeting = "Good Night\n🌌 ";
    }

    const greetingElement = document.getElementById("greeting");
    if (greetingElement) {
        greetingElement.textContent = greeting;
    }
});