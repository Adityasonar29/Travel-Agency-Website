(function () {
    function showVoyageLoader() {
        const overlay = document.getElementById('voyage-loading-overlay');
        if (!overlay) return;
        overlay.classList.add('is-visible');
        overlay.setAttribute('aria-hidden', 'false');
    }

    function hideVoyageLoader() {
        const overlay = document.getElementById('voyage-loading-overlay');
        if (!overlay) return;
        overlay.classList.remove('is-visible');
        overlay.setAttribute('aria-hidden', 'true');
    }

    window.showVoyageLoader = showVoyageLoader;
    window.hideVoyageLoader = hideVoyageLoader;
    window.addEventListener('pageshow', hideVoyageLoader);

    document.addEventListener('submit', function (event) {
        const form = event.target.closest('[data-voyage-loading-form]');
        if (!form || form.dataset.submitting === 'true') return;

        form.dataset.submitting = 'true';
        const dialog = form.closest('dialog');
        if (dialog) dialog.classList.add('is-submitting');
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.setAttribute('aria-busy', 'true');
        }
        showVoyageLoader();
    });

    if (new URLSearchParams(window.location.search).get('preview_loader') === '1') {
        showVoyageLoader();
    }
})();
