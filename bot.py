import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# 1. SERVER WEB PER ENTRARE IN SINTONIA CON RENDER E UPTIMEROBOT
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running!")

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
    raw_text = update.message.text.strip().upper()  # Gestisce sia 'd' che 'D'
    is_double = raw_text.endswith('D')
    
    # Isola i numeri rimuovendo le lettere e i simboli
    time_str = raw_text.replace("D", "").replace("/H", "").replace("/", "")
    
    # Formattazione dell'orario
    if len(time_str) <= 2:
        formatted_time = f"{time_str.zfill(2)}:00"
    elif len(time_str) == 3:
        formatted_time = f"0{time_str[0]}:{time_str[1:]}"
    elif len(time_str) == 4:
        formatted_time = f"{time_str[:2]}:{time_str[2:]}"
    else:
        formatted_time = time_str

    # Selezione del testo del sondaggio
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

# 3. FUNZIONE PRINCIPALE (Torna al Polling sicuro)
def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Errore: TELEGRAM_BOT_TOKEN non trovato!")
        return

    # Avvia l'unico server web in background per rispondere a UptimeRobot
    threading.Thread(target=run_server, daemon=True).start()

    # Avvia l'applicazione Telegram
    app = ApplicationBuilder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    
    # Accetta comandi numerici che terminano opzionalmente con 'd' o 'D'
    time_filter = filters.Regex(r"^/(h)?\d{1,4}[dD]?$")
    app.add_handler(MessageHandler(time_filter, handle_time_poll))

    print("Bot avviato con successo in modalita Polling!")
    app.run_polling()

if __name__ == '__main__':
    main()
    
