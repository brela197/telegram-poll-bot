import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import ApplicationBuilder, CommandHandler

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

async def start(update, context):
    await update.message.reply_text("Ciao! Il bot è attivo e i sondaggi sono pronti.")

# Comando per inviare il sondaggio (puoi adattare la domanda e le opzioni)
async def poll(update, context):
    question = "Qual è il tuo orario preferito o la tua preferenza per oggi?"
    options = ["Opzione 1", "Opzione 2", "Opzione 3"]
    
    await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question=question,
        options=options,
        is_anonymous=False
    )

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Errore: TELEGRAM_BOT_TOKEN non trovato!")
        return

    # Avvia il server web per Render in un thread separato
    threading.Thread(target=run_server, daemon=True).start()

    app = ApplicationBuilder().token(token).build()
    
    # Gestione dei comandi
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("poll", poll)) # Comando /poll per richiamare il sondaggio

    print("Bot avviato con successo!")
    app.run_polling()

if __name__ == '__main__':
    main()
    
