from jinja2 import Template, Environment
from flask import render_template_string, request

def render_user_content(content):
    return render_template_string(content)

def display_user_profile(user_data):
    bio = user_data.get('bio', '')
    
    html = f"""
    <div class="profile">
        <h1>{user_data['name']}</h1>
        <p>{bio}</p>
    </div>
        <html>
            <body>
                <header>Bienvenido {user_name}</header>
                <div id="custom">{custom_html}</div>
            </body>
        </html>
    <div class="comment">
        <p>{user_comment}</p>
    </div>
    """
    return html
