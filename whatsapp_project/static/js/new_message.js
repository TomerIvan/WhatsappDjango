$(document).ready(function() {
    let typingTimer;
    const doneTypingInterval = 500; // 0.5 seconds

    // Get the reply_to parameter from URL and handle recipient setting
    const replyTo = new URLSearchParams(window.location.search).get('reply_to');
    
    // If this is a reply, fetch the thread details and set the recipient
    if (replyTo) {
        $.ajax({
            url: '/api/messages/latest/',
            method: 'GET',
            success: function(response) {
                // Find the specific thread
                const thread = response.threads.find(t => t.thread_id.toString() === replyTo);
                
                if (thread && thread.messages.length > 0) {
                    const originalMessage = thread.messages[0];
                    
                    // If is_sender is true, set recipient to original recipient
                    // If is_sender is false, set recipient to original sender
                    const recipientName = originalMessage.is_sender ? 
                        originalMessage.recipient_name : 
                        originalMessage.sender_name;
                    
                    // Extract username from the name
                    fetchUserByName(recipientName);
                }
            },
            error: function(xhr) {
                console.error('Error fetching message details:', xhr);
            }
        });
    }
    
    function fetchUserByName(fullName) {
        // Extract the first part of the name (before the comma)
        const lastName = fullName.split(',')[0].trim();
        
        $.ajax({
            url: '/api/users/search/',
            method: 'GET',
            data: { username: lastName },  // Search by last name
            success: function(response) {
                if (response.users && response.users.length > 0) {
                    // Find the user with matching full name
                    const user = response.users.find(u => 
                        `${u.last_name}, ${u.first_name}` === fullName
                    );
                    
                    if (user) {
                        $('#recipient').val(user.username).prop('readonly', true);
                    }
                }
            },
            error: function(xhr) {
                console.error('Error fetching user details:', xhr);
            }
        });
    }
    
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
    
    // Username autocomplete
    $('#recipient').on('input', function() {
        clearTimeout(typingTimer);
        const $suggestions = $('#recipientSuggestions');
        
        if ($(this).val()) {
            typingTimer = setTimeout(function() {
                fetchUserSuggestions();
            }, doneTypingInterval);
        } else {
            $suggestions.hide().empty();
        }
    });
    
    function fetchUserSuggestions() {
        const username = $('#recipient').val();
        if (username.length < 2) return; // Minimum 2 characters before searching
        
        $.ajax({
            url: '/api/users/search/',
            method: 'GET',
            data: { username: username },
            success: function(response) {
                displaySuggestions(response.users);
            },
            error: function(xhr) {
                console.error('Error fetching user suggestions:', xhr);
            }
        });
    }
    
    function displaySuggestions(users) {
        const $suggestions = $('#recipientSuggestions');
        
        if (users.length === 0) {
            $suggestions.hide().empty();
            return;
        }
        
        const suggestionsHtml = users.map(user => `
            <div class="suggestion-item" data-username="${user.username}">
                ${user.last_name}, ${user.first_name} (${user.username})
            </div>
        `).join('');
        
        $suggestions.html(suggestionsHtml).show();
    }
    
    // Handle suggestion selection
    $(document).on('click', '.suggestion-item', function() {
        const username = $(this).data('username');
        $('#recipient').val(username);
        $('#recipientSuggestions').hide().empty();
    });
    
    // Hide suggestions when clicking outside
    $(document).on('click', function(e) {
        if (!$(e.target).closest('.recipient-input-container').length) {
            $('#recipientSuggestions').hide().empty();
        }
    });
    
    // Form submission
    $('#messageForm').on('submit', function(e) {
        e.preventDefault();
        
        const recipient = $('#recipient').val();
        const content = $('#content').val();
        
        if (!recipient || !content) {
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
    
    // Clear button
    $('#clearButton').click(function() {
        $('#content').val('').trigger('input');
        if (!$('#recipient').prop('readonly')) {
            $('#recipient').val('');
        }
        $('#recipientError, #contentError').text('');
    });
});