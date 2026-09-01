import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

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
    await update.message.reply_text("Ciao! Il bot è attivo. Usa ad esempio /8 o /730 per inviare il sondaggio.")

async def handle_time_poll(update, context):
    text = update.message.text.strip()
    
    # Rimuove sia "/h" che "/" iniziale per isolare solo i numeri
    time_str = text.replace("/h", "").replace("/", "")
    
    # Se inserisci solo l'ora da 1 a 2 cifre (es. /8 o /21), aggiunge in automatico i minuti :00
    if len(time_str) <= 2:
        formatted_time = f"{time_str.zfill(2)}:00"
    # Se inserisci 3 cifre (es. /730 -> 07:30)
    elif len(time_str) == 3:
        formatted_time = f"0{time_str[0]}:{time_str[1:]}"
    # Se inserisci 4 cifre (es. /1203 -> 12:03)
    elif len(time_str) == 4:
        formatted_time = f"{time_str[:2]}:{time_str[2:]}"
    else:
        formatted_time = time_str

    question = f"⏰ {formatted_time} ➡️ BOOST ARTICOLO ❤️ Ci siete?"
    # Opzioni con i quadratini colorati e sondaggio non anonimo (is_anonymous=False)
    options = ["🟩 Ci sono 💯💯💯", "🟥 No 🙂‍↔️  "]
    
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

    # Avvia il server web per Render (mantiene il bot sempre attivo)
    threading.Thread(target=run_server, daemon=True).start()

    app = ApplicationBuilder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    
    # Cattura sia i comandi corti (es. /8) che quelli completi (es. /730, /1203, /h1203)
    time_filter = filters.Regex(r"^/(h)?\d{1,4}$")
    app.add_handler(MessageHandler(time_filter, handle_time_poll))

    print("Bot avviato con successo!")
    app.run_polling()

if __name__ == '__main__':
    main()
    
