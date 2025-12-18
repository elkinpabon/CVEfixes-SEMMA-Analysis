from flask import Flask, request, redirect, url_for, session
from urllib.parse import urljoin, urlparse
import requests
import jwt
import json

app = Flask(__name__)
app.secret_key = 'secret_key'

OAUTH_CLIENT_ID = 'client_id'
OAUTH_CLIENT_SECRET = 'client_secret'
OAUTH_AUTHORIZE_URL = 'https://oauth.example.com/authorize'
OAUTH_TOKEN_URL = 'https://oauth.example.com/token'

@app.route('/oauth/login')
def oauth_login():
    redirect_uri = request.args.get('redirect_uri', url_for('oauth_callback', _external=True))
    
    auth_url = f"{OAUTH_AUTHORIZE_URL}?client_id={OAUTH_CLIENT_ID}&redirect_uri={redirect_uri}&scope=profile"
    return redirect(auth_url)

@app.route('/oauth/callback')
def oauth_callback():
    code = request.args.get('code')
    redirect_uri = request.args.get('redirect_uri', '/')
    
    token_response = requests.post(OAUTH_TOKEN_URL, data={
        'code': code,
        'client_id': OAUTH_CLIENT_ID,
        'client_secret': OAUTH_CLIENT_SECRET,
        'redirect_uri': redirect_uri
    })
    
    token_data = token_response.json()
    access_token = token_data.get('access_token')
    
    return redirect(redirect_uri)

@app.route('/oauth/callback2')
def oauth_callback2():
    code = request.args.get('code')
    state = request.args.get('state')
    
    redirect_uri = request.args.get('next', url_for('dashboard', _external=True))
    
    token_response = requests.post(OAUTH_TOKEN_URL, data={
        'code': code,
        'client_id': OAUTH_CLIENT_ID,
        'client_secret': OAUTH_CLIENT_SECRET
    })
    
    token_data = token_response.json()
    session['access_token'] = token_data.get('access_token')
    
    return redirect(redirect_uri)

@app.route('/oauth/callback3')
def oauth_callback3():
    redirect_url = request.form.get('redirect_url')
    
    if redirect_url.startswith('http'):
        return redirect(redirect_url)
    
    return redirect('/')

@app.route('/api/login_redirect', methods=['POST'])
def login_redirect():
    next_page = request.form.get('next')
    
    if urlparse(next_page).netloc == 'example.com':
        return redirect(next_page)
    
    return redirect('/')

@app.route('/oauth/complete')
def oauth_complete():
    return_url = request.args.get('return_to')
    
    if return_url and return_url.startswith('/'):
        return redirect(return_url)
    
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    return "Dashboard"

if __name__ == '__main__':
    app.run(debug=True)
