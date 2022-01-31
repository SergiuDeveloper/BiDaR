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
    suggestion_div.setAttribute("class", "border-0");

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

function fetch_autocomplete_suggestions(event){
    const target_element = event.target;
    const type = event.target.id.split("_")[0];
    let input = target_element.value;
    remove_error(target_element);
    if (input.trim() != '') {
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
            'input_text': input,
            "type": type
        }));
    }
};

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

function add_error(input){
    const parent = input.parentNode;
    const sibling = input.nextSibling;
    var error = document.createElement("div");
    error.classList = 'alert alert-danger';
    error.role = "alert";
    error.innerHTML = "Concept does not exist";
    parent.insertBefore(error,sibling);
}

function remove_error(input){
    var error = input.nextSibling;
    if (error.classList[1] == "alert-danger"){
        error.remove();
    }
}

function update_list(label, ref, section){
    const list = document.getElementById(`${section}_list`);
    var li = document.createElement("li");
    var a = document.createElement("a");
    var x = document.createElement("a");
    a.href = ref;
    a.innerHTML = label;
    x.innerHTML = " X"
    x.classList = "remove_data text-danger text-decoration-none"
    x.href = ""
    li.appendChild(a);
    li.appendChild(x);
    list.appendChild(li);
    queryAllFactsOnClick("network");
}

function add_data(event){
    const section = event.target.id.split("_")[1];
    const input = document.getElementById(section+'_input');
    var interest_ref = input.name;
    if (interest_ref == ""){
        add_error(input);
        return 0;
    }
    const name = document.getElementById("name").innerHTML;
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            var responseText = xmlHttp.responseText;
            var responceJSON = JSON.parse(responseText)
            if (responceJSON == false){
                add_error(input);
            }
            else{
                update_list(responceJSON["label"], responceJSON["ref"], section)
            }
            input.value = "";
        }
    }
    
    if (section == "Knows"){
        interest_ref = input.value;
    }

    xmlHttp.open('POST', `${URL}/add_data`, true);
    xmlHttp.setRequestHeader('Access-Control-Allow-Origin', '*');
    xmlHttp.send(JSON.stringify({
        'name': name,
        'data': interest_ref,
        "section": section
    }));

}

function remove_data(event){
    const section = event.target.parentNode.parentNode.id.split("_")[0];
    const name = "Andrei Ghiran"
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            var responseText = xmlHttp.responseText;
            var responceJSON = JSON.parse(responseText)
        }
    }
    const data_ref = event.target.previousElementSibling.href;
    xmlHttp.open('POST', `${URL}/remove_data`, true);
    xmlHttp.setRequestHeader('Access-Control-Allow-Origin', '*');
    xmlHttp.send(JSON.stringify({
        'name': "Andrei Ghiran",
        'data': data_ref,
        "section": section
    }));
}


const suggestion_elements = document.getElementsByClassName("suggestions");

for (var i = 0; i<suggestion_elements.length; i++){
    var element = suggestion_elements[i];
    element.addEventListener("input", debounce(function(e) {
        fetch_autocomplete_suggestions(e);
    }));    
}

const add_element = document.getElementsByClassName('add_to_list');


for (var i = 0; i<add_element.length; i++){
    var element = add_element[i];
    element.addEventListener("click", debounce(function(e) {
        add_data(e);
    })); 
}

const remove_element = document.getElementsByClassName('remove_data');
for (var i = 0; i<remove_element.length; i++){
    var element = remove_element[i];
    element.addEventListener("click", debounce(function(e) {
        remove_data(e);
    })); 
}