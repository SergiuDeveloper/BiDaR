const URL = 'http://localhost:8080'

function addPersonOnClick() {
    var nameInput = document.getElementById('nameInput').value;
    var ageInput = document.getElementById('ageInput').value;
    var genderInput = document.getElementById('genderInput').value;
    var countryInput = document.getElementById('countryInput').value;
    var cityInput = document.getElementById('cityInput').value;
    var jobTitleInput = document.getElementById('jobTitleInput').value;
    var languageInput = document.getElementById('languageInput').value;
    
    if (isNaN(parseInt(ageInput)) || parseInt(ageInput) < 0 ||
        nameInput.length == 0 ||
        genderInput.length == 0 ||
        countryInput.length == 0 ||
        cityInput.length == 0 ||
        jobTitleInput.length == 0 ||
        languageInput.length == 0
    ) {
        add_error(document.getElementById('nameInput'),"All data is mandatorry!");
        return;
    }

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            var responseText = xmlHttp.responseText;
            var responce = JSON.parse(responseText)
            console.log(responce);
            if (responce["message"] == "Error"){
                add_error(document.getElementById('nameInput'),"Error at user creation");
            }
            else if (responce["message"] == `User ${nameInput} already exists`){
                add_alert(document.getElementById('nameInput'), responce["message"], responce["ref"]);
            }
            else if (responce["message"] == "Success"){
                location.href = responce["ref"];
            }
            
        }
    }
    xmlHttp.open('POST', `${URL}/add_person`, true);
    xmlHttp.setRequestHeader('Access-Control-Allow-Origin', '*');
    xmlHttp.send(JSON.stringify({
        'name': nameInput,
        'age': ageInput,
        'gender': genderInput,
        'country': countryInput,
        'city': cityInput,
        'jobTitle': jobTitleInput,
        'language': languageInput,
    }));
}

function add_error(input, message){
    var error = document.getElementById(input.id.split("_")[0] +"_error");
    error.classList = 'alert alert-danger justify-content-center';
    error.role = "alert";
    error.innerHTML = message;
}

function remove_error(input, type){
    var error = document.getElementById(input.id.split("_")[0] +"_" + type);
    error.classList = "d-none"
}

function add_alert(input, message, ref){
    var alert = document.getElementById(input.id.split("_")[0] +"_alert");
    alert.classList = 'alert alert-warning justify-content-center';
    alert.role = "alert";
    alert.href = ref
    var a = document.createElement("a");
    a.href = ref;
    a.innerHTML = message;
    alert.appendChild(a);
}
 
const inputs = document.getElementsByClassName("user_data_input");
const first = inputs[0];
for (var i = 0; i<inputs.length; i++){
    var element = inputs[i];
    element.addEventListener("input", function(e) {
        remove_error(first, "error");
        remove_error(first, "alert");
    });    
}