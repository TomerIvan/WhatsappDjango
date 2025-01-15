// Constants for better maintainability
const FORM_CONFIG = {
    fields: {
        username: {
            selector: '#UserName',
            validations: [
                {
                    check: (value) => /^[A-Za-z]/.test(value),
                    errorMessage: 'User name must start with an English letter.'
                },
                {
                    check: (value) => !/^\s|\s$/.test(value),
                    errorMessage: 'Field cannot start or end with a space.'
                }
            ]
        },
        password: {
            selector: '#Password',
            validations: [
                {
                    check: (value) => !/\s/.test(value),
                    errorMessage: 'Password cannot contain any spaces.'
                },
                {
                    check: (value) => !/^\s|\s$/.test(value),
                    errorMessage: 'Field cannot start or end with a space.'
                }
            ]
        }
    },
    submitButton: '#Login',
    clearButton: '#Clear'
};

let isFieldValidating = {}; // Track validation state for each field

$(document).ready(function () {
    initializeFormValidation();
    redirectToRegistration();
    setupLoginHandler();
    setupCSRFToken();
    showsuccess();
});

function initializeFormValidation() {
    const $submitButton = $(FORM_CONFIG.submitButton);
    setButtonState($submitButton, false);

    Object.values(FORM_CONFIG.fields).forEach(field => {
        const $field = $(field.selector);
        const fieldId = $field.attr('id');
        isFieldValidating[fieldId] = false; // Initialize validation state

        $field.on('input', function () {
            if (isFieldValidating[fieldId]) {
                return; // Prevent new validation while one is in progress
            }

            isFieldValidating[fieldId] = true;
            setTimeout(() => {
                handleInputValidation($field);
                isFieldValidating[fieldId] = false;
            }, 300); // Debounce delay
        });

        $field.on('blur', function() {
            if (isFieldValidating[fieldId]) {
                return; // Prevent new validation while one is in progress
            }
            handleInputValidation($field);
        });
    });

    initializeClearButton();
}

function initializeClearButton() {
    $(FORM_CONFIG.clearButton).on('click', function () {
        $('.form__field').val('');
        $('.error-label').remove();
        setButtonState($(FORM_CONFIG.submitButton), false);
    });
}

function handleInputValidation($field) {
    const fieldId = $field.attr('id');
    const fieldConfig = Object.values(FORM_CONFIG.fields).find(config => config.selector === '#' + fieldId);

    if (!fieldConfig) return;

    const value = $field.val();
    hideError($field);

    if (value.length === 0) {
        showError($field, `${$field.attr('placeholder')} is required.`);
        setButtonState($(FORM_CONFIG.submitButton), false);
        return;
    }

    for (const validation of fieldConfig.validations) {
        if (!validation.check(value)) {
            showError($field, validation.errorMessage);
            setButtonState($(FORM_CONFIG.submitButton), false);
            return;
        }
    }

    validateAllFields();
}

function validateAllFields() {
    const $submitButton = $(FORM_CONFIG.submitButton);
    const isValid = Object.values(FORM_CONFIG.fields).every(field => {
        const $field = $(field.selector);
        const value = $field.val();

        if (value.length === 0) return false;
        return field.validations.every(validation => validation.check(value));
    });

    setButtonState($submitButton, isValid);
}

function setButtonState($button, enabled) {
    $button
        .prop('disabled', !enabled)
        .animate({ opacity: enabled ? 1 : 0.5 }, 200)
        .css({
            cursor: enabled ? 'pointer' : 'not-allowed',
            pointerEvents: enabled ? 'auto' : 'none'
        });
}

function showError($field, message) {
    hideError($field);

    const $errorLabel = $('<div>', {
        class: 'error-label',
        css: {
            color: 'red',
            fontWeight: '400',
            fontSize: '14px',
            display: 'none'
        },
        text: message
    });

    $field.after($errorLabel);
    $errorLabel.slideDown(300);
}

function hideError($field) {
    $field.next('.error-label').remove();
}

function showWarning(message) {
    const $warning = $('.warning');
    
    // If there's a success message showing (green background)
    if ($warning.is(':visible') && $warning.css('background-color') !== 'var(--warning-red)') {
        // First hide the success message
        $warning.slideUp(300, function() {
            // After it's hidden, change the color and text
            $(this)
                .css('background-color', 'var(--warning-red)')
                .text(message)
                // Then show the new error message
                .slideDown(300, function() {
                    // Hide after 3 seconds
                    setTimeout(() => {
                        $(this).slideUp(300, function() {
                            $(this).text("");
                        });
                    }, 3000);
                });
        });
    } else {
        // Normal warning behavior when no success message is showing
        $warning
            .css('background-color', 'var(--warning-red)')
            .text(message)
            .slideDown(300);
        
        setTimeout(() => {
            $warning.slideUp(300, function() {
                $(this).text("");
            });
        }, 3000);
    }
}

function redirectToRegistration() {
    $('#Registration').on('click', function () {
        window.location.href = 'http://127.0.0.1:8000/registration/';
    });
}

function setupLoginHandler() {
    $('#Login').on('click', function (e) {
        e.preventDefault();

        $('.error-label').remove();
        const username = $('#UserName').val().trim();
        const password = $('#Password').val().trim();

        $.ajax({
            url: '/login/',
            type: 'POST',
            headers: { 'X-CSRFToken': getCSRFToken() },
            data: { username: username, password: password },
            dataType: 'json',
            success: function (response) {
                if (response.success) {
                    window.location.href = response.redirect_url;
                }
            },
            error: function (xhr) {
                const response = xhr.responseJSON || {};
                if (response.error) {
                    showWarning(response.error);
                } else {
                    showWarning('An unknown error occurred.');
                }
            }
        });
    });
}

function setupCSRFToken() {
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                xhr.setRequestHeader("X-CSRFToken", getCSRFToken());
            }
        }
    });
}

function showsuccess() {
    var success_msg = $('.Success').text().trim();
    if (success_msg == 'Registration successful!') {
        $(".warning").css('background-color', 'green');
        $(".warning").slideDown(400, function () {
            setTimeout(function () {
                $(".warning").slideUp(300, function() {
                    $(".warning").css('background-color', 'var(--warning-red)');
                });
            }, 5000);

            setTimeout(function () {
                $('.Success').empty();
            }, 5300);
        });
    }
    else if (success_msg == 'Your session has expired. Please log in again.'){
        $(".warning").css('background-color', 'var(--warning-red)');
        $(".warning").css('display', 'flex');
        $(".warning").css('justify-content', 'center');
        
        $("p.warning").css('width', '100%');
        $(".warning").slideDown(400, function () {
            setTimeout(function () {
                $(".warning").slideUp(300, function() {
                    $(".warning").css('background-color', 'var(--warning-red)');
                });
            }, 5000);
        })
    }

}


function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
        const trimmedCookie = cookie.trim();
        if (trimmedCookie.startsWith(`${name}=`)) {
            return decodeURIComponent(trimmedCookie.slice(name.length + 1));
        }
    }
    return null;
}