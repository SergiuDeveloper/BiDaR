from flask import Flask
from flask_cors import CORS


PORT = 80

app = Flask(__name__)
CORS(app)


@app.get('/')
def serve_index_html():
    with open('resources/index.html', 'r', encoding='utf8') as file:
        return file.read()

@app.get('/js/base.js')
def serve_base_js():
    with open('resources/js/base.js', 'r', encoding='utf8') as file:
        return file.read()

@app.get('/js/vis.js')
def serve_vis_js():
    with open('resources/js/vis.js', 'r', encoding='utf8') as file:
        return file.read()

@app.get('/css/base.css')
def serve_base_css():
    with open('resources/css/base.css', 'r', encoding='utf8') as file:
        return file.read()

@app.get('/css/vis.css')
def serve_vis_css():
    with open('resources/css/vis.css', 'r', encoding='utf8') as file:
        return file.read()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)