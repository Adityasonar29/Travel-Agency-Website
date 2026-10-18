(function () {
    const overlay = document.getElementById('voyage-loading-overlay');
    const showButton = document.querySelector('[data-loader-show]');
    const replayButton = document.querySelector('[data-loader-replay]');

    function showLoader() {
        overlay.classList.remove('is-leaving');
        overlay.classList.add('is-visible');
        overlay.setAttribute('aria-hidden', 'false');
    }

    function hideLoader() {
        overlay.classList.remove('is-visible');
        overlay.setAttribute('aria-hidden', 'true');
    }

    function replayLoader() {
        showLoader();
        window.setTimeout(hideLoader, 2200);
    }

    showButton.addEventListener('click', showLoader);
    replayButton.addEventListener('click', replayLoader);
})();
