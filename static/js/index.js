window.addEventListener('load', init);

let popup;
let logout;

function init () {

    popup = document.querySelector('#popup');

    logout = document.querySelector('#logout')
    logout.addEventListener('click', buttonClickHandler);
}

function buttonClickHandler (e) {

        popup.classList.remove('hide');

    if (logout.dataset.visible === 'false') {

        console.log('iofios')

        popup.classList.add('popup');

        let h2 = document.createElement('h2');
        h2.innerHTML = "Are you sure you want to log out?";
        popup.appendChild(h2);

        let p = document.createElement('p');
        p.innerHTML = "No worries! All your data is saved";
        popup.appendChild(p);

        let buttonDiv = document.createElement('div');
        buttonDiv.classList.add('logout-choose')
        popup.appendChild(buttonDiv);

        let logoutForm = document.createElement('form');
        logoutForm.action = "index.html";
        logoutForm.classList.add('logout-form')
        buttonDiv.appendChild(logoutForm);

        let logoutButton = document.createElement('button');
        logoutButton.innerHTML = 'Log out';
        logoutButton.type = "submit";
        logoutButton.classList.add('logout-buttons');
        logoutButton.classList.add('btn');
        logoutButton.classList.add('btn-danger');
        logoutForm.appendChild(logoutButton);

        let rejectButton = document.createElement('button');
        rejectButton.innerHTML = 'No';
        // rejectButton.classList.add('logout-buttons');
        rejectButton.classList.add('btn');
        rejectButton.classList.add('btn-success');
        rejectButton.addEventListener('click', rejectButtonClickHandler)
        buttonDiv.appendChild(rejectButton);

        logout.dataset.visible = 'true'

    }
}

function rejectButtonClickHandler (e) {

    popup.classList.add('hide')

}
