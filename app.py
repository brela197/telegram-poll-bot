import os
import threading
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler

# Configura il server web per UptimeRobot
app = Flask(__name__)

@app.route('/')
def home():
    return "Il bot è online!"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# Qui metti il token del tuo bot (o lo prendi dalle variabili d'ambiente)
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

def run_bot():
    # Nota: Assicurati che qui dentro ci sia la logica del tuo bot, 
    # oppure se hai il codice principale in bot.py possiamo importarlo.
    pass

if __name__ == "__main__":
    # Avvia il server web in un "filo" separato per UptimeRobot
    t = threading.Thread(target=run_web)
    t.start()
    
    # Qui facciamo partire il bot
    # (Dimmi: nel tuo bot.py usi python-telegram-bot?)
    
