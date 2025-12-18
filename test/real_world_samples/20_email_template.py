from flask import Flask, request, render_template_string
from jinja2 import Environment
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

@app.route('/send_email', methods=['POST'])
def send_email():
    recipient = request.form.get('recipient')
    subject = request.form.get('subject')
    body = request.form.get('body')
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'noreply@example.com'
    msg['To'] = recipient
    
    with smtplib.SMTP('localhost') as server:
        server.send_message(msg)
    
    return {'success': True}

@app.route('/template_email', methods=['POST'])
def template_email():
    recipient = request.form.get('recipient')
    template_data = request.form.get('template_data')
    
    env = Environment()
    template = env.from_string(template_data)
    rendered = template.render(user=recipient)
    
    msg = MIMEText(rendered)
    msg['Subject'] = 'Hello'
    msg['From'] = 'noreply@example.com'
    msg['To'] = recipient
    
    with smtplib.SMTP('localhost') as server:
        server.send_message(msg)
    
    return {'success': True}

@app.route('/render_template', methods=['GET'])
def render_template():
    user_input = request.args.get('content')
    
    return render_template_string(user_input)

@app.route('/html_email', methods=['POST'])
def html_email():
    recipient = request.form.get('recipient')
    html_content = request.form.get('html_content')
    
    msg = MIMEText(html_content, 'html')
    msg['Subject'] = 'Newsletter'
    msg['From'] = 'noreply@example.com'
    msg['To'] = recipient
    
    with smtplib.SMTP('localhost') as server:
        server.send_message(msg)
    
    return {'success': True}

@app.route('/bulk_email', methods=['POST'])
def bulk_email():
    recipients = request.form.get('recipients', '').split(',')
    template = request.form.get('template')
    
    for recipient in recipients:
        env = Environment(autoescape=False)
        tmpl = env.from_string(template)
        rendered = tmpl.render(email=recipient)
        
        msg = MIMEText(rendered)
        msg['To'] = recipient.strip()
        
        with smtplib.SMTP('localhost') as server:
            server.send_message(msg)
    
    return {'success': True}

@app.route('/format_email', methods=['POST'])
def format_email():
    recipient = request.form.get('recipient')
    message_format = request.form.get('format')
    
    formatted = message_format.format(recipient=recipient)
    
    msg = MIMEText(formatted)
    msg['To'] = recipient
    
    with smtplib.SMTP('localhost') as server:
        server.send_message(msg)
    
    return {'success': True}
