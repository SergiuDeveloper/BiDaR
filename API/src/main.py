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
    text = request.get_json(force=True)['text']

    nouns = [str(noun) for noun in TextProcessor.extract_nouns(text)]
    language = TextProcessor.detect_language(text)
    resultsLimit = int(request.args.get('resultsLimit'))
    searchDepth = int(request.args.get('searchDepth'))

    sparql_processor = SparqlProcessor()
    query_data = sparql_processor.query_information_multithreaded(nouns, language, resultsLimit, searchDepth)

    return jsonify(query_data)

@app.post('/query_all_data')
def query_all_data():
    name = request.get_json(force=True)['name']
    result = ontology_processor.query_all_data(name)
    return jsonify(result)

@app.post('/query_interests')
def query_interests():
    name = request.get_json(force=True)['name']
    result = ontology_processor.query_interests(name)
    return jsonify(result)

@app.post('/add_person')
def add_person():
    result = ontology_processor.add_person(
        request.get_json(force=True)['name'],
        request.get_json(force=True)['age'],
        request.get_json(force=True)['gender'],
        request.get_json(force=True)['country'],
        request.get_json(force=True)['city'],
        request.get_json(force=True)['jobTitle'],
        request.get_json(force=True)['language'],
        request.get_json(force=True)['friends'] if "friends" in request.get_json(force=True).keys() else [],
        request.get_json(force=True)['interests'] if "interests" in request.get_json(force=True).keys() else [],
        request.get_json(force=True)['skills'] if "skills" in request.get_json(force=True).keys() else [],
        request.get_json(force=True)['favoriteArtists'] if "favoriteArtists" in request.get_json(force=True).keys() else []
    )
    return jsonify(result)

@app.get('/get_all_persons')
def get_all_persons():
    persons = ontology_processor.get_all_persons()
    return jsonify(persons)

def exceptions_hook(exc_type, exc_value, exc_traceback, ontology_processor):
    ontology_processor.deactivate_backup_daemon()

    traceback.print_exception(exc_type, exc_value, exc_traceback)

@app.post('/add_data')
def add_data():
    user_name = request.get_json(force=True)["name"]
    data = request.get_json(force=True)["data"]
    section = request.get_json(force=True)["section"]
    result = ontology_processor.add_data_to_user(user_name,data,section)
    return jsonify(result)

@app.post('/remove_data')
def remove_data():
    user_name = request.get_json(force=True)["name"]
    data = request.get_json(force=True)["data"]
    section = request.get_json(force=True)["section"]
    result = ontology_processor.remove_data_from_user(user_name,data,section)
    return jsonify(result)

@app.post("/autocomplete_suggestions")
def get_autocomplete_suggestions():
    input_text = request.get_json(force=True)["input_text"]
    type = request.get_json(force=True)["type"]
    sparql_processor = SparqlProcessor()

    result = sparql_processor.get_autocomplete_suggestions(input_text, type)
    return jsonify(result)

if __name__ == '__main__':
    ontology_processor = OntologyProcessor(ONTOLOGY_FILE_PATH, ONTOLOGY_FORMAT)
    ontology_processor.activate_backup_daemon(1)

    sys.excepthook = lambda exc_type, exc_value, exc_traceback: exceptions_hook(exc_type, exc_value, exc_traceback, ontology_processor)

    app.run(host='0.0.0.0', port=PORT)
