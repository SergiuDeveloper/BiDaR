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
        element_div.innerHTML = arr[i];
        element_div.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";  // insert a input field that will hold the current array item's value
        // execute a function when someone clicks on the item value (DIV element)
        element_div.addEventListener("click", function (e) {
            inp.value = this.getElementsByTagName("input")[0].value;  // insert the value for the autocomplete text field
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
    const target_element = event.target;
    let input = target_element.value;
    if (input.trim() != '') {
        input = input.replace(/ /gi, "_");
        let query_params = new URLSearchParams()
        query_params.set('search_text', input)
        const api_url = `${window.location.origin}/profile/preference_suggestions/?${query_params}`
        fetch(api_url)
            .then(r => r.json())
            .then(t => autocomplete(target_element, t))
            .catch(e => console.log(e));
    }
};

function debounce(func, wait = 150, early = false) {
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

// const element = document.querySelector('.suggestions');
// console.log("aaaaaaaaaaaaaaaaaaaaaaaaaaaa");
// element.addEventListener("input", debounce(function(e) {
//     fetch_autocomplete_user_suggestions(e);
// }));
