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
    await update.message.reply_text("Ciao! Il bot è attivo. Scrivi ad esempio /h2100 o /h0730 per inviare il sondaggio.")

# Gestore dinamico per qualsiasi orario (es. /h700, /h2100, /h2330)
async def handle_time_poll(update, context):
    text = update.message.text.strip()
    time_str = text.replace("/h", "")
    
    # Formatta l'orario in modo pulito (es. da 2100 a 21:00 o da 700 a 07:00)
    if len(time_str) == 3:
        formatted_time = f"0{time_str[0]}:{time_str[1:]}"
    elif len(time_str) == 4:
        formatted_time = f"{time_str[:2]}:{time_str[2:]}"
    else:
        formatted_time = time_str

    question = f"⏰ {formatted_time} ➡️ BOOST ARTICOLO ❤️ Ci siete?"
    options = ["Presente", "Assente"]
    
    await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question=question,
        options=options,
        is_anonymous=True
    )

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Errore: TELEGRAM_BOT_TOKEN non trovato!")
        return

    # Avvia il server web per Render
    threading.Thread(target=run_server, daemon=True).start()

    app = ApplicationBuilder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    
    # Cattura in automatico qualsiasi comando che inizia per /h seguito da 3 o 4 numeri
    time_filter = filters.Regex(r"^/h\d{3,4}$")
    app.add_handler(MessageHandler(time_filter, handle_time_poll))

    print("Bot avviato con successo!")
    app.run_polling()

if __name__ == '__main__':
    main()
  
