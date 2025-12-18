from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import sqlite3
import subprocess

class TelegramBot:
    def __init__(self, token):
        self.app = Application.builder().token(token).build()
        self.db = sqlite3.connect(':memory:')
        
        # Registra handlers
        self.app.add_handler(CommandHandler("search", self.search_command))
        self.app.add_handler(CommandHandler("exec", self.exec_command))
        self.app.add_handler(MessageHandler(filters.TEXT, self.handle_message))
    
    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            return
        
        search_term = ' '.join(context.args)
        
        query = f"SELECT * FROM users WHERE username LIKE '%{search_term}%'"
        
        cursor = self.db.cursor()
        cursor.execute(query)
        
        results = cursor.fetchall()
        await update.message.reply_text(f"Resultados: {results}")
    
    async def exec_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            return
        
        cmd = ' '.join(context.args)
        
        result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        output = result.communicate()[0]
        
        await update.message.reply_text(output.decode())
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_input = update.message.text
        
        query = f"INSERT INTO messages (user_id, text) VALUES ({update.message.from_user.id}, '{user_input}')"
        
        cursor = self.db.cursor()
        cursor.execute(query)
        
        response = f"Mensaje recibido: {user_input}"
        await update.message.reply_text(response)

class NotificationHandler:
    def build_notification(self, user_message: str):
        notification = f"⚠️ {user_message}"
        return notification
    
    def format_alert(self, alert_text: str):
        from jinja2 import Template
        
        template = Template(alert_text)
        return template.render()
