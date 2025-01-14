// Constants for better maintainability
const FORM_CONFIG = {
    fields: {
        username: {
            selector: '#UserName',
            validations: [
                {
                    check: (value) => /^[A-Za-z]/.test(value),
                    errorMessage: 'Username must start with an English letter.'
                },
                {
                    check: (value) => !/^\s|\s$/.test(value),
                    errorMessage: 'Field cannot start or end with a space.'
                }
            ]
        },
        firstName: {
            selector: '#FirstName',
            validations: [
                {
                    check: (value) => value.length > 0,
                    errorMessage: 'First name is required.'
                },
                {
                    check: (value) => !/^\s|\s$/.test(value),
                    errorMessage: 'Field cannot start or end with a space.'
                },
                {
                    check: (value) => /^[A-Za-zÀ-ÖØ-öø-ÿ]+$/.test(value),
                    errorMessage: 'First name can only contain letters.'
                }
            ]
        },
        lastName: {
            selector: '#LastName',
            validations: [
                {
                    check: (value) => value.length > 0,
                    errorMessage: 'Last name is required.'
                },
                {
                    check: (value) => !/^\s|\s$/.test(value),
                    errorMessage: 'Field cannot start or end with a space.'
                },
                {
                    check: (value) => /^[A-Za-zÀ-ÖØ-öø-ÿ]+$/.test(value),
                    errorMessage: 'Last name can only contain letters.'
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
    submitButton: '#Register',
    clearButton: '#Clear'
};

let isFieldValidating = {}; // Track validation state for each field

$(document).ready(function () {
    initializeFormValidation();
    redirectToLogin();
    CheckErrorMessage();
});

function initializeFormValidation() {
    const $submitButton = $(FORM_CONFIG.submitButton);
    setButtonState($submitButton, false);

    Object.values(FORM_CONFIG.fields).forEach(field => {
        const $field = $(field.selector);
        const fieldId = $field.attr('id');
        isFieldValidating[fieldId] = false; // Initialize validation state

        $field.on('input', function () {
            if (isFieldValidating[fieldId]) return;
            isFieldValidating[fieldId] = true;
            setTimeout(() => {
                handleInputValidation($field);
                isFieldValidating[fieldId] = false;
            }, 300);
        });

        $field.on('blur', function () {
            if (isFieldValidating[fieldId]) return;
            handleInputValidation($field);
        });
    });

    initializeClearButton();
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

function initializeClearButton() {
    $(FORM_CONFIG.clearButton).on('click', function () {
        $('.form__field').val('');
        $('.error-label').remove();
        setButtonState($(FORM_CONFIG.submitButton), false);
    });
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

function redirectToLogin() {
    $('#Login').on('click', function () {
        window.location.href = 'http://127.0.0.1:8000/login/';
    });
}

function CheckErrorMessage() {
    $(document).ready(function () {
        var error_msg = $('.Error').text().trim();
        if (error_msg.length > 0) { // Check if the message is not empty. This is the fix.
            $(".warning").slideDown(400, function () {
                setTimeout(function () {
                    $(".warning").slideUp();
                }, 5000);
            });
        }
    });
}