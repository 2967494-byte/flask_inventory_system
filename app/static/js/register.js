document.addEventListener('DOMContentLoaded', function () {
    const innInput = document.getElementById('inn-field');
    const findButton = document.getElementById('inn-search-btn');

    if (!innInput || !findButton) return;

    findButton.addEventListener('click', function (e) {
        e.preventDefault();

        const inn = innInput.value.trim();
        if (!inn) {
            alert('Пожалуйста, введите ИНН');
            return;
        }

        // Show loading state
        const originalText = findButton.textContent;
        findButton.disabled = true;
        findButton.textContent = 'Поиск...';

        fetch('/api/dadata/company', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
            },
            body: JSON.stringify({ inn: inn })
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    return;
                }

                // Populate fields
                const nameInput = document.querySelector('input[name="company_name"]');
                if (nameInput) {
                    nameInput.value = data.name || '';
                    // Trigger input event in case there are listeners
                    nameInput.dispatchEvent(new Event('input', { bubbles: true }));
                }

                if (data.address) {
                    const addressInput = document.querySelector('input[name="legal_address"]');
                    if (addressInput) addressInput.value = data.address;
                }

                if (data.kpp) {
                    const kppInput = document.querySelector('input[name="kpp"]');
                    if (kppInput) kppInput.value = data.kpp;
                }

                if (data.ogrn) {
                    const ogrnInput = document.querySelector('input[name="ogrn"]');
                    if (ogrnInput) ogrnInput.value = data.ogrn;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Ошибка при поиске организации');
            })
            .finally(() => {
                findButton.disabled = false;
                findButton.textContent = originalText;
            });
    });
});
