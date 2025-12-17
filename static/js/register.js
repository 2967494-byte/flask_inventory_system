document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const captchaInput = document.getElementById('register-captcha-input');
    const csrfToken = document.querySelector('input[name="csrf_token"]').value;

    if (form && captchaInput) {
        // Clear validity on input so user can type
        captchaInput.addEventListener('input', function () {
            this.setCustomValidity('');
        });

        form.addEventListener('submit', function (event) {
            event.preventDefault(); // Stop currently simple submission

            const captchaValue = captchaInput.value;

            // Basic client-side check if empty (though 'required' attr handles this usually)
            if (!captchaValue) {
                captchaInput.setCustomValidity('Введите код с картинки');
                captchaInput.reportValidity();
                return;
            }

            fetch('/validate_captcha', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ captcha: captchaValue })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.valid) {
                        captchaInput.setCustomValidity('');
                        form.submit();
                    } else {
                        captchaInput.setCustomValidity('Неверный код с картинки');
                        captchaInput.reportValidity();

                        // Optional: refresh captcha automatically or let user do it? 
                        // Usually better to let user retry or refresh if they want.
                        // But if it's wrong, maybe the image is hard to read.
                        // Let's just focus on the field validity for now.
                    }
                })
                .catch(error => {
                    console.error('Error validating captcha:', error);
                    // Fallback to server side validation if fetch fails?
                    // Or show generic error
                    captchaInput.setCustomValidity('Ошибка проверки. Попробуйте обновить страницу.');
                    captchaInput.reportValidity();
                });
        });
    }
});
