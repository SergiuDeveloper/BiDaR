const URL = 'http://localhost:8080'
const DjangURL = 'http://localhost:8000'


function queryFactsOnClick(networkElementId) {
    clearRelatedInterestList();
    var textInput = document.getElementById('textInput').value;
    var maxResults = document.getElementById('maxResults').value;
    var searchDepth = document.getElementById('searchDepth').value;

    if (isNaN(parseInt(maxResults)) || isNaN(parseInt(searchDepth)) || parseInt(maxResults) <= 0 || parseInt(searchDepth) <= 0 || textInput.length == 0) {
        return;
    }

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            var responseText = xmlHttp.responseText;
            var triples = JSON.parse(responseText)["graph_data"];
            var nouns = JSON.parse(responseText)["nouns"];
            populateGraph(networkElementId, triples);
            getRelatedInterests(nouns);
        }
    }
    xmlHttp.open('POST', `${URL}/semantic_web_data?resultsLimit=${maxResults}&searchDepth=${searchDepth}`, true);
    xmlHttp.setRequestHeader('Access-Control-Allow-Origin', '*');
    xmlHttp.send(JSON.stringify({
        'text': textInput
    }));
}

function getRelatedInterests(nouns) {
    var nameInput = document.getElementById('pick_user').value;

    if (nameInput.length == 0) {
        return;
    }

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            var responseText = xmlHttp.responseText;
            var triples = JSON.parse(responseText)
            populateRelatedInterestList(triples)
        }
    }
    xmlHttp.open('POST', `${URL}/related_to_interests`, true);
    xmlHttp.setRequestHeader('Access-Control-Allow-Origin', '*');
    xmlHttp.send(JSON.stringify({
        'name': nameInput,
        "nouns": nouns
    }));
}

function populateRelatedInterestList(data){
    const list = document.getElementById("related_interst_list");
    const keys = Object.keys(data);
    const length = keys.length;
    for (i = 0; i<length;i++){
        if (data[keys[i]].length > 0){
            const li = document.createElement("li");
            const a = document.createElement("h4");
            const div = document.createElement("div")
            li.setAttribute("class","m-2 list-group-item h-25 border");
            a.setAttribute("id", keys[i]+"_related_interests_title")
            div.setAttribute("class","mt-4 border h-75");
            div.setAttribute("id",keys[i]+"_related_interests");
            li.appendChild(a);
            li.appendChild(div);
            list.appendChild(li);
            a.innerHTML = "Interest related to "+ keys[i];
            populateGraph(div.id,data[keys[i]]);
        }
    }
}

function clearRelatedInterestList(){
    const list = document.getElementById("related_interst_list");
    list.innerHTML = "";
}

function populateGraph(networkElementId, triples) {
    var predicates = {};

    var entitiesSet = new Set();
    for (const triple of triples) {
        entitiesSet.add(triple[0]);
        entitiesSet.add(triple[2]);

        if (!([triple[0], triple[2]] in predicates)) {
            predicates[[triple[0], triple[2]]] = []
        }
        predicates[[triple[0], triple[2]]].push(triple[1]);
    }
    var entitiesList = [...entitiesSet];

    var entityIndexMap = {}
    var nodesList = []
    for (var i = 0; i < entitiesList.length; i++) {
        var entity = entitiesList[i];
        nodesList.push({
            id: i,
            label: entity
        });
        entityIndexMap[entity] = i;
    }
    var nodes = new vis.DataSet(nodesList);

    var edgesList = []
    for (const triple of triples) {
        var fromNode = entityIndexMap[triple[0]];
        var toNode = entityIndexMap[triple[2]];
        edgesList.push({
            from: fromNode,
            to: toNode,
            label: predicates[[triple[0], triple[2]]].shift(),
            width: 1
        });
    }
    var edges = new vis.DataSet(edgesList);

    var container = document.getElementById(networkElementId);
    var data = {
        nodes: nodes,
        edges: edges
    };
    var options = {
        edges: {
            arrows: {
                to: {
                    enabled: true,
                    scaleFactor: 1,
                    type: "arrow"
                }
            }
        }
    };

    new vis.Network(container, data, options);
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

window.onload = getPersons();