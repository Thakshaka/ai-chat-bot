# bot.py
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from dotenv import load_dotenv
from threading import Thread
from flask import Flask

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")

# Configure the generative model
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

def generate_content(full_prompt: str) -> str:
    try:
        response = model.generate_content(full_prompt)
        return response.text if hasattr(response, 'text') else "Sorry, I couldn't generate a response."
    except Exception as e:
        return f"There was an error generating the response: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.first_name
    await update.message.reply_text(f"Hello {user_id}! I am a chatbot. How can I help you today?")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    response_text = generate_content(user_message)
    await update.message.reply_text(response_text)

# Telegram bot thread
def run_telegram():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    app.run_polling()

# Flask HTTP server for health checks
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return "Alive"

if __name__ == "__main__":
    # Start Telegram bot in background
    Thread(target=run_telegram).start()

    # Start Flask as main process (port 8000)
    flask_app.run(host='0.0.0.0', port=8000)
