const URL = 'http://localhost:8080'


function queryFactsOnClick(networkElementId) {
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
            var triples = JSON.parse(responseText)
            populateGraph(networkElementId, triples)
        }
    }
    xmlHttp.open('POST', `${URL}/semantic_web_data?resultsLimit=${maxResults}&searchDepth=${searchDepth}`, true);
    xmlHttp.setRequestHeader('Access-Control-Allow-Origin', '*');
    xmlHttp.send(textInput);
}

function addPersonOnClick(networkElementId) {
    var nameInput = document.getElementById('nameInput').value;
    var ageInput = document.getElementById('ageInput').value;
    var genderInput = document.getElementById('genderInput').value;
    var countryInput = document.getElementById('countryInput').value;
    var cityInput = document.getElementById('cityInput').value;
    var jobTitleInput = document.getElementById('jobTitleInput').value;
    var languageInput = document.getElementById('languageInput').value;
    var friendsInput = document.getElementById('friendsInput').value;
    var interestsInput = document.getElementById('interestsInput').value;
    var skillsInput = document.getElementById('skillsInput').value;
    var favoriteArtistsInput = document.getElementById('favoriteArtistsInput').value;

    friendsInput = friendsInput.split(/, |,/);
    interestsInput = interestsInput.split(/, |,/);
    skillsInput = skillsInput.split(/, |,/);
    favoriteArtistsInput = favoriteArtistsInput.split(/, |,/);

    if (isNaN(parseInt(ageInput)) || parseInt(ageInput) < 0 ||
        nameInput.length == 0 ||
        genderInput.length == 0 ||
        countryInput.length == 0 ||
        cityInput.length == 0 ||
        jobTitleInput.length == 0 ||
        languageInput.length == 0 ||
        friendsInput.length == 0 ||
        interestsInput.length == 0 ||
        skillsInput.length == 0 ||
        favoriteArtistsInput.length == 0
    ) {
        return;
    }

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            var responseText = xmlHttp.responseText;
            var triples = JSON.parse(responseText)
            populateGraph(networkElementId, triples)
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
        'friends': friendsInput,
        'interests': interestsInput,
        'skills': skillsInput,
        'favoriteArtists': favoriteArtistsInput
    }));
}

function populateGraph(networkElementId, triples) {
    var predicates = {};

    var entitiesSet = new Set();
    for (const triple of triples) {
        entitiesSet.add(triple[0]);
        entitiesSet.add(triple[2]);

        predicates[[triple[0], triple[2]]] = triple[1];
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
            label: predicates[[triple[0], triple[2]]],
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