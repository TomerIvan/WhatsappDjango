$(document).ready(function() {
    let typingTimer;
    const doneTypingInterval = 500; // 0.5 seconds
    
    // Character counter and validation
    $('#content').on('input', function() {
        const maxLength = 1024;
        const currentLength = $(this).val().length;
        const $charCount = $('#charCount');
        const $contentError = $('#contentError');
        
        $charCount.text(currentLength);
        
        if (currentLength > maxLength) {
            $charCount.parent().addClass('error');
            $contentError.text(`Message is too long. Maximum length is ${maxLength} characters.`);
            $('#sendButton').prop('disabled', true);
        } else {
            $charCount.parent().removeClass('error');
            $contentError.text('');
            $('#sendButton').prop('disabled', false);
        }
    });
    
    // Username autocomplete - disabled since we only want to chat with current user
    $('#recipient').prop('readonly', true);
    
    // Form submission
    $('#messageForm').on('submit', function(e) {
        e.preventDefault();
        
        const recipient = $('#recipient').val();
        const content = $('#content').val();
        const replyTo = new URLSearchParams(window.location.search).get('reply_to');
        const currentUser = $('#currentUsername').val(); // Add a hidden input with current user's username
        
        if (!recipient || !content) {
            return;
        }
        
        // Prevent sending message to self
        if (recipient === currentUser) {
            $('#recipientError').text("You cannot send a message to yourself.");
            return;
        }
        
        const data = {
            recipient: recipient,
            content: content,
            reply_to: replyTo
        };
        
        $.ajax({
            url: '/api/messages/send/',
            method: 'POST',
            data: data,
            headers: {
                'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                window.location.href = '/messages/';
            },
            error: function(xhr) {
                const error = xhr.responseJSON;
                if (error.field === 'recipient') {
                    $('#recipientError').text(error.error);
                } else if (error.field === 'content') {
                    $('#contentError').text(error.error);
                }
            }
        });
    });
    
    // Clear button - modified to not clear readonly recipient
    $('#clearButton').click(function() {
        $('#content').val('').trigger('input');
        $('#recipientError, #contentError').text('');
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