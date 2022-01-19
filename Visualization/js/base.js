function submitOnClick(networkElementId) {
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
    xmlHttp.open('POST', `http://localhost:8080//semantic_web_data?resultsLimit=${maxResults}&searchDepth=${searchDepth}`, true);
    xmlHttp.setRequestHeader('Access-Control-Allow-Origin', '*');
    xmlHttp.send(textInput);
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