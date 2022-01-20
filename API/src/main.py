import sys
import traceback

from flask import Flask, request, jsonify
from flask_cors import CORS

from rdflib.namespace import FOAF

from lib.TextProcessor import TextProcessor
from lib.SparqlProcessor import SparqlProcessor
from lib.OntologyProcessor import OntologyProcessor


PORT = 8080

ONTOLOGY_FILE_PATH = '../data/ontology.rdf'
ONTOLOGY_FORMAT = 'application/rdf+xml'


app = Flask(__name__)
CORS(app)


@app.post('/semantic_web_data')
def semantic_web_data():
    text = request.data.decode('utf-8')

    nouns = [str(noun) for noun in TextProcessor.extract_nouns(text)]
    language = TextProcessor.detect_language(text)
    resultsLimit = int(request.args.get('resultsLimit'))
    searchDepth = int(request.args.get('searchDepth'))

    sparql_processor = SparqlProcessor()
    query_data = sparql_processor.query_information_multithreaded(nouns, language, resultsLimit, searchDepth)
    return jsonify(query_data)

@app.post('/query_all_data')
def query_all_data():
    name = request.json['name']
    result = ontology_processor.query_all_data(name)
    return jsonify(result)

@app.post('/query_interests')
def query_interests():
    name = request.json['name']
    result = ontology_processor.query_interests(name)
    return jsonify(result)

@app.post('/add_person')
def add_person():
    result = ontology_processor.add_person(
        request.json['name'],
        request.json['age'],
        request.json['gender'],
        request.json['country'],
        request.json['city'],
        request.json['jobTitle'],
        request.json['language'],
        request.json['friends'],
        request.json['interests'],
        request.json['skills'],
        request.json['favorite_artists']
    )
    return jsonify(result)

def exceptions_hook(exc_type, exc_value, exc_traceback, ontology_processor):
    ontology_processor.deactivate_backup_daemon()

    traceback.print_exception(exc_type, exc_value, exc_traceback)


if __name__ == '__main__':
    ontology_processor = OntologyProcessor(ONTOLOGY_FILE_PATH, ONTOLOGY_FORMAT)
    ontology_processor.activate_backup_daemon(1)

    sys.excepthook = lambda exc_type, exc_value, exc_traceback: exceptions_hook(exc_type, exc_value, exc_traceback, ontology_processor)

    app.run(host='0.0.0.0', port=PORT)