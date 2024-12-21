let deleteDataButton = document.querySelector('#clear-data')

let tableForSingers = document.querySelector('#table-for-singers');
deleteDataButton.addEventListener('click', (e) => {
    e.preventDefault()
    let inputField = document.querySelector('#musician')
    if (inputField.value !== '')
        inputField.value = ''
    tableForSingers.innerHTML = ''
    document.querySelector(".add-data").remove()
    // document.querySelector("#limit").value = 1
    // document.querySelector(".changed-stat").innerText = '1/10'

    let url = new URL(window.location)
    url.searchParams.delete('musician')
    window.history.pushState({}, '', url);
    let existingMessage = document.querySelector('.message-display');
    if (existingMessage) {
        return;
    }
    let displayAnnounce = document.createElement('div')
    displayAnnounce.classList.add('message-display')
    let textParagraph = document.createElement('p')
    textParagraph.textContent = 'Ви видалили дані'
    displayAnnounce.appendChild(textParagraph)
    document.body.appendChild(displayAnnounce)
    displayAnnounce.classList.add('fade-out');
    setTimeout(() => {
        displayAnnounce.classList.add('fade');
        setTimeout(func => {
            displayAnnounce.remove()
        }, 1000)
    }, 1000)
})
let countOfMusician = document.querySelector('.range-input')
let choseAtThatMoment = document.querySelector('.changed-stat')

choseAtThatMoment.addEventListener('DOMContentLoaded',()=>{
  choseAtThatMoment.innerText =`${countOfMusician.value}/${countOfMusician.max}`
})
countOfMusician.addEventListener('change',()=>{
    choseAtThatMoment.innerText =`${countOfMusician.value}/${countOfMusician.max}`
})