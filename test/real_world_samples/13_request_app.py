import requests
from urllib.parse import urljoin
from flask import Flask, request, render_template_string, redirect

app = Flask(__name__)

@app.route('/fetch')
def fetch_content():
    url = request.args.get('url', 'http://example.com')
    response = requests.get(url, timeout=5)
    return response.text

@app.route('/proxy')
def proxy():
    target = request.args.get('target')
    path = request.args.get('path', '/')
    full_url = urljoin(target, path)
    response = requests.get(full_url)
    return response.content

@app.route('/callback')
def callback():
    redirect_to = request.args.get('redirect')
    return redirect(redirect_to)

@app.route('/fetch-api')
def fetch_api():
    endpoint = request.args.get('endpoint')
    api_url = f"https://api.example.com/{endpoint}"
    response = requests.get(api_url)
    return response.json()

@app.route('/render')
def render():
    template = request.args.get('template')
    return render_template_string(template)
