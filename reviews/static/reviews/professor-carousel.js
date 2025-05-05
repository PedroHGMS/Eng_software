document.addEventListener('DOMContentLoaded', function () {
    const container = document.querySelector('.carousel-container');
    const leftButton = document.querySelector('.carousel-button.left');
    const rightButton = document.querySelector('.carousel-button.right');
    const card = document.querySelector('.professor-card');

    if (!container || !leftButton || !rightButton || !card) return;

    const cardWidth = card.offsetWidth + 20;
    const SCROLL_CARDS = 3;

    leftButton.addEventListener('click', () => {
        container.scrollBy({ left: -cardWidth * SCROLL_CARDS, behavior: 'smooth' });
    });

    rightButton.addEventListener('click', () => {
        container.scrollBy({ left: cardWidth * SCROLL_CARDS, behavior: 'smooth' });
    });
});
