import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# 1. SERVER WEB STRUTTURATO PER IMPEDIRE LO SLEEP DI RENDER
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        # Risposta HTML reale per ingannare Render e i sistemi di ping
        self.wfile.write(b"<html><head><title>Bot Status</title></head><body><h1>Bot is actively running!</h1></body></html>")

def run_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# 2. FUNZIONI DEL BOT TELEGRAM
async def start(update, context):
    await update.message.reply_text(
        "Ciao! Il bot è attivo.\n\n"
        "Esempi comandi:\n"
        "• `/8` o `/730` per sondaggio Singolo\n"
        "• `/8D` o `/730D` per sondaggio Doppio"
    )

async def handle_time_poll(update, context):
    try:
        raw_text = update.message.text.strip().upper()  # Gestisce sia 'd' che 'D'
        is_double = raw_text.endswith('D')
        
        # Isola i numeri rimuovendo lettere e simboli
        time_str = raw_text.replace("D", "").replace("/H", "").replace("/", "")
        
        # Formattazione orario
        if len(time_str) <= 2:
            formatted_time = f"{time_str.zfill(2)}:00"
        elif len(time_str) == 3:
            formatted_time = f"0{time_str[0]}:{time_str[1:]}"
        elif len(time_str) == 4:
            formatted_time = f"{time_str[:2]}:{time_str[2:]}"
        else:
            formatted_time = time_str

        # Testo del sondaggio in base alla scelta
        if is_double:
            question = f"⏰ {formatted_time} ➡️ BOOST ARTICOLO DOPPIO 💖💖 Ci siete??"
            options = ["🟩 Siiii 💯💯💯", "🟥 No 🫠"]
        else:
            question = f"⏰ {formatted_time} ➡️ BOOST ARTICOLO ❤️ Ci siete?"
            options = ["🟩 Ci sono 💯💯💯", "🟥 No 🙂‍↔️  "]
        
        await context.bot.send_poll(
            chat_id=update.effective_chat.id,
            question=question,
            options=options,
            is_anonymous=False
        )
    except Exception as e:
        print(f"Errore durante la gestione del sondaggio: {e}")

# 3. FUNZIONE PRINCIPALE
def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Errore: TELEGRAM_BOT_TOKEN non trovato!")
        return

    # Avvia l'unico server web rinforzato in background per UptimeRobot
    threading.Thread(target=run_server, daemon=True).start()

    # Avvia l'applicazione Telegram
    app = ApplicationBuilder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    
    # Accetta comandi numerici che terminano opzionaImente con 'd' o 'D'
    time_filter = filters.Regex(r"^/(h)?\d{1,4}[dD]?$")
    app.add_handler(MessageHandler(time_filter, handle_time_poll))

    print("Bot avviato con successo in modalita Polling!")
    app.run_polling()

if __name__ == '__main__':
    main()
    
