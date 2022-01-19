from flask import Flask, request, jsonify
from flask_cors import CORS

from lib.TextProcessor import TextProcessor
from lib.SparqlProcessor import SparqlProcessor


PORT = 8080


app = Flask(__name__)
CORS(app)


@app.post('/semantic_web_data')
def semantic_web_data():
    text = request.data.decode('utf-8')

    nouns = [str(noun) for noun in TextProcessor.extract_nouns(text)]
    language = TextProcessor.detect_language(text)
    resultsLimit = int(request.args.get('resultsLimit'))
    searchDepth = int(request.args.get('searchDepth'))

    query_data = SparqlProcessor.query_information_multithreaded(nouns, language, resultsLimit, searchDepth)
    query_data = list(query_data)

    return jsonify(query_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)