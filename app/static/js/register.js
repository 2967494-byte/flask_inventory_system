document.addEventListener('DOMContentLoaded', function () {
    const innInput = document.getElementById('inn-field');
    const findButton = document.getElementById('inn-search-btn');

    if (!innInput || !findButton) return;

    findButton.addEventListener('click', function (e) {
        e.preventDefault();
        console.log('[DEBUG] INN search button clicked');

        const inn = innInput.value.trim();
        if (!inn) {
            console.log('[DEBUG] Empty INN field');
            alert('Пожалуйста, введите ИНН');
            return;
        }

        console.log('[DEBUG] Searching for INN:', inn);

        // Show loading state
        const originalText = findButton.textContent;
        findButton.disabled = true;
        findButton.textContent = 'Поиск...';

        const csrfTokenNode = document.querySelector('input[name="csrf_token"]');
        if (!csrfTokenNode) {
            console.error('[DEBUG] CSRF token not found!');
            alert('Ошибка безопасности: CSRF токен не найден. Перезагрузите страницу.');
            findButton.disabled = false;
            findButton.textContent = originalText;
            return;
        }

        console.log('[DEBUG] CSRF Token found, sending request to /api/dadata/company');

        fetch('/api/dadata/company', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfTokenNode.value
            },
            body: JSON.stringify({ inn: inn })
        })
            .then(response => {
                console.log('[DEBUG] Response received, status:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('[DEBUG] Data parsed:', data);
                if (data.error) {
                    console.warn('[DEBUG] Server returned error:', data.error);
                    alert(data.error);
                    return;
                }

                // Populate fields
                const nameInput = document.querySelector('input[name="company_name"]');
                if (nameInput) {
                    nameInput.value = data.name || '';
                    nameInput.dispatchEvent(new Event('input', { bubbles: true }));
                    console.log('[DEBUG] Company name populated:', data.name);
                }

                // ... rest of population logic
            })
            .catch(error => {
                console.error('[DEBUG] Fetch error:', error);
                alert('Ошибка при поиске организации: ' + error.message);
            })
            .finally(() => {
                findButton.disabled = false;
                findButton.textContent = originalText;
                console.log('[DEBUG] Search finished');
            });
    });
});
