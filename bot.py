import os
import threading
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# 1. SERVER WEB PER IMPEDIRE LO SLEEP DI RENDER
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"<html><head><title>Bot Status</title></head><body><h1>Bot is actively running!</h1></body></html>")

def run_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# 2. FUNZIONI DEL BOT TELEGRAM
async def start(update, context):
    await update.message.reply_text(
        "Ciao! Il bot è attivo con grafiche casuali.\n\n"
        "• `/8` o `/730` per sondaggio Singolo (Random)\n"
        "• `/8D` o `/730D` per sondaggio Doppio (Random)"
    )

async def handle_time_poll(update, context):
    try:
        raw_text = update.message.text.strip().upper()
        is_double = raw_text.endswith('D')
        
        # Isola i numeri dell'orario
        time_str = raw_text.replace("D", "").replace("/H", "").replace("/", "")
        
        if len(time_str) <= 2:
            formatted_time = f"{time_str.zfill(2)}:00"
        elif len(time_str) == 3:
            formatted_time = f"0{time_str[0]}:{time_str[1:]}"
        elif len(time_str) == 4:
            formatted_time = f"{time_str[:2]}:{time_str[2:]}"
        else:
            formatted_time = time_str

        # ELENCO DELLE OPZIONI GRAFICHE CASUALI
        if is_double:
            # SONDAGGI DOPPI (Comandi con la 'D' finale)
            varianti_doppie = [
                {
                    "question": f"📊 SONDAGGIO ATTIVO\n\n⏰ Orario: {formatted_time}\n🔥 Obiettivo: DOPPIO BOOST 💖💖\n\nRaddoppiamo la forza, ci siete?? 👇",
                    "options": ["🟩 Siiii! 🚀🚀", "🟥 Oggi no 🫠"]
                },
                {
                    "question": f"💥 SUPER BOOST DOPPIO 💥\n\n📌 Appuntamento alle ore {formatted_time}\n💖 Due articoli da spingere al massimo!\n\nCarichi per la doppietta? 🔥",
                    "options": ["⚡ DOPPIETTA PRONTA 🟩", "💤 Passo il turno 🟥"]
                },
                {
                    "question": f"⌛ NOTIFICA PROGRAMMATA\n\n• Slot Orario: {formatted_time}\n• Attività: Boost Doppia Recensione 💖💖\n\nConferma la tua presenza qui sotto:",
                    "options": ["🟢 Confermo per entrambi", "🔴 Impossibilitato"]
                }
            ]
            scelta = random.choice(varianti_doppie)
        else:
            # SONDAGGI SINGOLI (Comandi normali)
            varianti_singole = [
                {
                    "question": f"📊 SONDAGGIO ATTIVO\n\n⏰ Orario: {formatted_time}\n🎯 Obiettivo: BOOST ARTICOLO ❤️\n\nCi siete per supportare il post? 👇",
                    "options": ["🟩 Ci sono! 💯", "🟥 Non riesco 🚫"]
                },
                {
                    "question": f"⚡ TEAM BOOST ⚡\n\n📌 Appuntamento alle ore {formatted_time}\n❤️ Lasciamo il segno sull'articolo!\n\nPronti a cliccare? 🚀",
                    "options": ["✅ PRESENTE 🟩", "❌ ASSENTE 🟥"]
                },
                {
                    "question": f"⌛ NOTIFICA PROGRAMMATA\n\n• Slot Orario: {formatted_time}\n• Attività: Boost Articolo Dedicato ❤️\n\nConferma la tua presenza qui sotto:",
                    "options": ["🟢 Confermo disponibilità", "🔴 Non disponibile"]
                }
            ]
            scelta = random.choice(varianti_singole)
        
        # Invia il sondaggio scelto casualmente
        await context.bot.send_poll(
            chat_id=update.effective_chat.id,
            question=scelta["question"],
            options=scelta["options"],
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

    threading.Thread(target=run_server, daemon=True).start()

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    
    time_filter = filters.Regex(r"^/(h)?\d{1,4}[dD]?$")
    app.add_handler(MessageHandler(time_filter, handle_time_poll))

    print("Bot avviato con successo in modalita Polling!")
    app.run_polling()

if __name__ == '__main__':
    main()

    print("Bot avviato con successo in modalita Polling!")
    app.run_polling()

if __name__ == '__main__':
    main()
    
