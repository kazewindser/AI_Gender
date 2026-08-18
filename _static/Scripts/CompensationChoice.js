(() => {
    const cards = Array.from(document.querySelectorAll('[data-choice-card]'));

    function updateSelection() {
        cards.forEach(card => {
            const radio = card.querySelector('.choice-radio');
            card.classList.toggle('selected', radio.checked);
        });
    }

    cards.forEach(card => {
        card.querySelector('.choice-radio').addEventListener(
            'change',
            updateSelection
        );
    });

    updateSelection();
})();
