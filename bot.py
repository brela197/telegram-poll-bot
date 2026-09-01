import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram import Update

# 1. FUNZIONI DEL BOT TELEGRAM
async def start(update, context):
    await update.message.reply_text(
        "Ciao! Il bot è attivo in modalità Webhook.\n\n"
        "Esempi comandi:\n"
        "• `/8` o `/730` per sondaggio Singolo\n"
        "• `/8D` o `/730D` per sondaggio Doppio"
    )

async def handle_time_poll(update, context):
    raw_text = update.message.text.strip().upper()
    is_double = raw_text.endswith('D')
    time_str = raw_text.replace("D", "").replace("/H", "").replace("/", "")
    
    if len(time_str) <= 2:
        formatted_time = f"{time_str.zfill(2)}:00"
    elif len(time_str) == 3:
        formatted_time = f"0{time_str[0]}:{time_str[1:]}"
    elif len(time_str) == 4:
        formatted_time = f"{time_str[:2]}:{time_str[2:]}"
    else:
        formatted_time = time_str

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

# 2. CONFIGURAZIONE PRINCIPALE
def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Errore: TELEGRAM_BOT_TOKEN non trovato!")
        return

    # Recupera l'URL dell'applicazione assegnato da Render (es. https://telegram-poll-bot-vtzq.onrender.com)
    # NOTA: Configura una variabile d'ambiente chiamata RENDER_EXTERNAL_URL su Render, oppure incolla direttamente la stringa.
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if not render_url:
        # Se non hai impostato la variabile, sostituisci qui il tuo URL reale tra le virgolette
        render_url = "https://telegram-poll-bot-vtzq.onrender.com"

    port = int(os.environ.get('PORT', 10000))

    # Inizializza l'applicazione del bot
    app = ApplicationBuilder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    time_filter = filters.Regex(r"^/(h)?\d{1,4}[dD]?$")
    app.add_handler(MessageHandler(time_filter, handle_time_poll))

    print("Avvio del bot in modalità Webhook...")
    
    # Questo singolo comando avvia sia il server web che l'ascolto di Telegram in modo nativo!
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=token,  # Usa il token come percorso sicuro per ricevere i dati da Telegram
        webhook_url=f"{render_url}/{token}"
    )

if __name__ == '__main__':
    main()
    
