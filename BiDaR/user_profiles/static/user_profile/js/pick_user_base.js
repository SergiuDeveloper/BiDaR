const URL = 'http://localhost:8080'

function debounce(func, wait = 350, early = false) {
    let timeout;
    return function (...args) {
        const context = this;
        const isEarlyEnable = !timeout && early;
        const executor = function () {
            timeout = null;
            !early && func.apply(context, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(executor, wait);
        isEarlyEnable && func.apply(context, args);
    };
}

function getPersons() {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            var responseText = xmlHttp.responseText;
            var persons = JSON.parse(responseText);
            var select = document.getElementById('pick_user');

            for (var i = 0; i < select.options.length; i++) {
                select.remove(i);
            }

            for (var i = 0; i < persons.length; i++) {
                select.options[i] = new Option(persons[i][0], persons[i][1]);
            }
        }
    }
    xmlHttp.open('GET', `${URL}/get_all_persons`, true);
    xmlHttp.setRequestHeader('Access-Control-Allow-Origin', '*');
    xmlHttp.send(null);
}

function redirectToUserProfile(){
    var input = document.getElementById("pick_user");
    ref = input.value;
    location.href = ref;
}

const button = document.getElementById("go_to_profile");
button.addEventListener("click", redirectToUserProfile);

window.onload = getPersons();
