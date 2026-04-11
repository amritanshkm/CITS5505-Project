document.addEventListener('DOMContentLoaded', () => {

    // Utility: Show Error
    function showError(inputElement, errorElementId, message) {
        inputElement.classList.add('is-invalid');
        inputElement.classList.remove('is-valid');
        const errorDiv = document.getElementById(errorElementId);
        if (errorDiv) {
            errorDiv.textContent = message;
        }
    }

    // Utility: Show Success
    function showSuccess(inputElement) {
        inputElement.classList.remove('is-invalid');
        inputElement.classList.add('is-valid');
    }

    // Utility: Validate Email format
    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    }

    // --- Login Form Validation ---
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function (event) {
            let isValid = true;

            const emailInput = document.getElementById('email');
            const passwordInput = document.getElementById('password');

            // Validate Email (prevent blank and check format)
            if (emailInput.value.trim() === '') {
                showError(emailInput, 'emailError', 'Email is required.');
                isValid = false;
            } else if (!isValidEmail(emailInput.value.trim())) {
                showError(emailInput, 'emailError', 'Please enter a valid email address.');
                isValid = false;
            } else {
                showSuccess(emailInput);
            }

            // Validate Password (prevent blank)
            if (passwordInput.value.trim() === '') {
                showError(passwordInput, 'passwordError', 'Password is required.');
                isValid = false;
            } else {
                showSuccess(passwordInput);
            }

            if (!isValid) {
                event.preventDefault(); // Prevent form submission
            }
        });
    }

    // --- Registration Form Validation ---
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function (event) {
            let isValid = true;

            const nameInput = document.getElementById('userName');
            const emailInput = document.getElementById('regEmail');
            const passwordInput = document.getElementById('regPassword');
            const confirmInput = document.getElementById('confirmPassword');

            // Validate Name
            if (nameInput.value.trim() === '') {
                showError(nameInput, 'nameError', 'Full Name is required.');
                isValid = false;
            } else {
                showSuccess(nameInput);
            }

            // Validate Email
            if (emailInput.value.trim() === '') {
                showError(emailInput, 'regEmailError', 'Email is required.');
                isValid = false;
            } else if (!isValidEmail(emailInput.value.trim())) {
                showError(emailInput, 'regEmailError', 'Please enter a valid email address.');
                isValid = false;
            } else {
                showSuccess(emailInput);
            }

            // Validate Password
            if (passwordInput.value.trim() === '') {
                showError(passwordInput, 'regPasswordError', 'Password is required.');
                isValid = false;
            } else if (passwordInput.value.length < 8) {
                showError(passwordInput, 'regPasswordError', 'Password must be at least 8 characters long.');
                isValid = false;
            } else {
                showSuccess(passwordInput);
            }

            // Validate Confirm Password
            if (confirmInput.value.trim() === '') {
                showError(confirmInput, 'confirmPasswordError', 'Please confirm your password.');
                isValid = false;
            } else if (confirmInput.value !== passwordInput.value) {
                showError(confirmInput, 'confirmPasswordError', 'Passwords do not match.');
                isValid = false;
            } else {
                showSuccess(confirmInput);
            }

            if (!isValid) {
                event.preventDefault();
            }
        });
    }

    // --- Global Validation Helpers for Later Use (Event Forms) ---
    // These will be used when we create create_event.html
    window.validateEventDate = function(dateString, inputElement, errorElementId) {
        if (!dateString) return false;
        const selectedDate = new Date(dateString);
        const today = new Date();
        today.setHours(0, 0, 0, 0); // Normalize today's date

        if (selectedDate < today) {
            showError(inputElement, errorElementId, 'Event date cannot be in the past.');
            return false;
        }
        showSuccess(inputElement);
        return true;
    };

    window.validateRequiredField = function(inputElement, errorElementId, fieldName) {
        if (inputElement.value.trim() === '') {
            showError(inputElement, errorElementId, `${fieldName} is required.`);
            return false;
        }
        showSuccess(inputElement);
        return true;
    };

});
