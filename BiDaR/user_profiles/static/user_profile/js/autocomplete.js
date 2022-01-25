const URL = 'http://localhost:8080'

// the autocomplete function takes two arguments, the text field element and an array of possible autocompleted values
function autocomplete(inp, arr) {
    // a function to classify an item as "active"
    function addActive(autocomplete_list) {
        // start by removing the "active" class on all items
        if (!autocomplete_list) return false;
            removeActive(autocomplete_list);
        if (currentFocus >= autocomplete_list.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (autocomplete_list.length - 1);
        autocomplete_list[currentFocus].classList.add("autocomplete-active");  // add class "autocomplete-active"
    };

    // a function to remove the "active" class from all autocomplete items
    function removeActive(autocomplete_list) {
        for (var i = 0; i < autocomplete_list.length; i++) {
            autocomplete_list[i].classList.remove("autocomplete-active");
        }
    };

    // close all autocomplete lists in the document, except the one passed as an argument
    function closeAllLists(element) {
        var autocomplete_items = document.getElementsByClassName("autocomplete-items");
        for (var i = 0; i < autocomplete_items.length; i++) {
            if (element != autocomplete_items[i] && element != inp) {
                autocomplete_items[i].parentNode.removeChild(autocomplete_items[i]);
            }
        }
    };

    var currentFocus;
    var suggestion_div, element_div, i, val = inp.value;

    // close any already open lists of autocompleted values
    closeAllLists();
    if (!val) { return false; }
    currentFocus = -1;

    // create a DIV element that will contain the items (values)
    suggestion_div = document.createElement("DIV");
    suggestion_div.setAttribute("id", inp.id + "autocomplete-list");
    suggestion_div.setAttribute("class", "autocomplete-items");

    // append the DIV element as a child of the autocomplete container
    inp.parentNode.appendChild(suggestion_div);

    for (i = 0; i < arr.length; i++) {
        // create a DIV element for each matching element
        element_div = document.createElement("DIV");
        element_div.innerHTML = arr[i]["label"]["value"];
        element_div.innerHTML += "<input type='hidden' name='" + arr[i]["ref"]["value"] +"' value='" + arr[i]["label"]["value"] + "'>";  // insert a input field that will hold the current array item's value
        // execute a function when someone clicks on the item value (DIV element)
        element_div.addEventListener("click", function (e) {
            inp.value = this.getElementsByTagName("input")[0].value;  // insert the value for the autocomplete text field
            inp.name = this.getElementsByTagName("input")[0].name;
            closeAllLists();  // close the list of autocompleted values, (or any other open lists of autocompleted values
        });
        suggestion_div.appendChild(element_div);
    }

    // execute a function presses a key on the keyboard
    inp.addEventListener("keydown", function (event) {
        var autocomplete_list = document.getElementById(this.id + "autocomplete-list");
        if (autocomplete_list) autocomplete_list = autocomplete_list.getElementsByTagName("div");
        if (event.keyCode == 40) {
            // If the arrow DOWN key is pressed, increase the currentFocus variable
            currentFocus++;
            addActive(autocomplete_list);  // and and make the current item more visible
        } else if (event.keyCode == 38) {
            // If the arrow UP key is pressed, decrease the currentFocus variable
            currentFocus--;
            // and and make the current item more visible
            addActive(autocomplete_list);
        } else if (event.keyCode == 13) {
            // If the ENTER key is pressed, prevent the form from being submitted
            event.preventDefault();
            if (currentFocus > -1) {
                // and simulate a click on the "active" item
                if (autocomplete_list) autocomplete_list[currentFocus].click();
            }
        }
    });

    // execute a function when someone clicks in the document
    document.addEventListener("click", function (event) {
        closeAllLists(event.target);
    });
};

function fetch_autocomplete_user_suggestions(event){
    console.log("call");
    const target_element = event.target;
    let input = target_element.value;
    if (input.trim() != '') {
        input = input.replace(/ /gi, "_");
        let query_params = new URLSearchParams()
        query_params.set('search_text', input)
        const api_url = `${URL}/autocomplete_suggestions`;
        var xmlHttp = new XMLHttpRequest();
        xmlHttp.onreadystatechange = function() {
            if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
                var responseText = xmlHttp.responseText;
                var json_response = JSON.parse(responseText)
                autocomplete(target_element, json_response);
            }
        }
        xmlHttp.open('POST', api_url, true);
        xmlHttp.setRequestHeader('Access-Control-Allow-Origin', '*');
        xmlHttp.send(JSON.stringify({
            'input_text': input
        }));
    }
};

function debounce(func, wait = 250, early = false) {
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

function update_interests(label, ref){
    const list = document.getElementById("interest_list");
    var li = document.createElement("li");
    var a = document.createElement("a");
    a.href = ref;
    a.innerHTML = label;
    li.appendChild(a);
    list.appendChild(li);
    queryAllFactsOnClick("network");
}

function add_interest(event){
    const input = document.getElementById('interest_input');
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            var responseText = xmlHttp.responseText;
            var responceJSON = JSON.parse(responseText)
            const label = input.value; 
            update_interests(responceJSON["label"], responceJSON["ref"])
            // console.log(responceJSON["label"]);
        }
    }
    // const input = document.getElementById('interest_input');
    const interest_ref = input.name;
    xmlHttp.open('POST', `${URL}/add_interest`, true);
    xmlHttp.setRequestHeader('Access-Control-Allow-Origin', '*');
    xmlHttp.send(JSON.stringify({
        'name': "Andrei Ghiran",
        'interest': interest_ref
    }));

}
console.log( document.querySelector('.suggestions'));
const element1 = document.querySelector('.suggestions');
element1.addEventListener("input", debounce(function(e) {
    fetch_autocomplete_user_suggestions(e);
}));

const element2 = document.querySelector('.addInterests');
element2.addEventListener("click", debounce(function(e) {
    add_interest(e);
}));