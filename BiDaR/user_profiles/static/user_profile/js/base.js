

function queryAllFactsOnClick(networkElementId) {
    var nameInput = document.getElementById('name').innerHTML;
    console.log(nameInput)
    if (nameInput.length == 0) {
        return;
    }

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            var responseText = xmlHttp.responseText;
            var triples = JSON.parse(responseText)
            console.log(triples)
            populateGraph(networkElementId, triples)
        }
    }
    xmlHttp.open('POST', `${URL}/query_all_data`, true);
    xmlHttp.setRequestHeader('Access-Control-Allow-Origin', '*');
    xmlHttp.send(JSON.stringify({
        'name': nameInput
    }));
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

window.onload = debounce(function(e) {
    queryAllFactsOnClick("network");
});