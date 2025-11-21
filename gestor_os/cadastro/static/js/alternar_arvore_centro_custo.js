document.addEventListener('DOMContentLoaded', function() {
    const toggles = document.querySelectorAll('.tree-toggle');

    toggles.forEach(toggle => {
        toggle.addEventListener('click', () => {
            toggle.classList.toggle('active');
            const nested = toggle.nextElementSibling;
            if (nested) {
                nested.style.display = nested.style.display === 'block' ? 'none' : 'block';
            }
        });
    });
});
