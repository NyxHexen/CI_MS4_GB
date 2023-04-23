// Game/DLC card animation event handling
let gameCards = document.querySelectorAll('.game')

gameCards.forEach(card => {
    card.addEventListener('mouseover', (e) => {
        card.classList.add('flip')
    })
    card.addEventListener('mouseout', (e) => {
        card.classList.remove('flip')
    })
})