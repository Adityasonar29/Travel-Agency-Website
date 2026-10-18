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

    if (new URLSearchParams(window.location.search).get('preview_loader') === '1') {
        showVoyageLoader();
    }
})();
