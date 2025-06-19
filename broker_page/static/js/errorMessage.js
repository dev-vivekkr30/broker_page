(() => {
    'use strict';

    const form = document.getElementById('broker-form');
    const eyeBtn = document.getElementById('eye-btn');

    form.addEventListener('submit', event => {
        if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();

            eyeBtn.style.borderColor = '#dc3545';
        }

        form.classList.add('was-validated');
    });
})();
