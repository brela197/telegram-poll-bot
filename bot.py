import os
import threading
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# 1. SERVER WEB PER IMPEDIRE LO SLEEP DI RENDER (Gestisce GET e HEAD)
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"<html><head><title>Bot Status</title></head><body><h1>Bot is actively running!</h1></body></html>")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

def run_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# 2. FUNZIONI DEL BOT TELEGRAM
async def start(update, context):
    await update.message.reply_text(
        "Ciao! Il bot è attivo con grafiche super semplici e casuali.\n\n"
        "• `/8` o `/730` per sondaggio Singolo (Semplificato Random)\n"
        "• `/8D` o `/730D` per sondaggio Doppio (Semplificato Random)\n"
        "• `/8I` o `/730I` per sondaggio Anonimo Con Messaggio Info (Nuovo) 📝"
    )

async def handle_time_poll(update, context):
    try:
        raw_text = update.message.text.strip().upper()
        
        # Riconosce il tipo di sondaggio dalla lettera finale
        is_double = raw_text.endswith('D')
        is_info = raw_text.endswith('I')
        
        # Isola i numeri dell'orario rimuovendo le lettere D, I, H e la barra /
        time_str = raw_text.replace("D", "").replace("I", "").replace("/H", "").replace("/", "")
        
        # Formattazione dell'orario
        if len(time_str) <= 2:
            formatted_time = f"{time_str.zfill(2)}:00"
        elif len(time_str) == 3:
            formatted_time = f"0{time_str[0]}:{time_str[1:]}"
        elif len(time_str) == 4:
            formatted_time = f"{time_str[:2]}:{time_str[2:]}"
        else:
            formatted_time = time_str

        # Inizializziamo le variabili del sondaggio
        question = ""
        options = []
        anonimo = False  # Di default i vecchi sondaggi restano NON anonimi

        # CONTROLLO E CREAZIONE DEL TIPO DI SONDAGGIO
        if is_info:
            # 🆕 NUOVO SONDAGGIO ANONIMO CON MESSAGGIO INFO (Preso dalla foto)
            anonimo = True
            question = (
                f"⏰ {formatted_time} ➡️ˢᴼᴼᴺ BOOST ARTICOLO ❤️ CON MESSAGGIO INFO ✉️\n\n"
                f"🧧 Accessibile solo a 10 link max 🧧 Inviare messaggi reali all'articolo/no emoticon 🚨"
            )
            options = ["Yesss 🍊🍊🍊", "✖️"]
            
        elif is_double:
            # SONDAGGI DOPPI (Comandi con la 'D' finale)
            varianti_doppie = [
                {
                    "question": f"🚀 DOPPIO BOOST DELLE {formatted_time} 💖💖\n\nPartecipi al doppio boost di adesso? Clicca sotto! 👇",
                    "options": ["🟩 Sì, partecipo a entrambi! 💯", "🟥 No, salto questo turno"]
                },
                {
                    "question": f"⏰ ORE {formatted_time} ➡️ DOPPIO BOOST 💖💖\n\nVota sotto se ci sei adesso: 👇",
                    "options": ["🟩 CI SONO PER ENTRAMBI! 🔥", "🟥 NON CI SONO ❌"]
                },
                {
                    "question": f"👋 Ragazzi, c'è il DOPPIO BOOST! (Ore {formatted_time}) 💖💖\n\nChi vuole fare doppietta di visualizzazioni adesso? 👇",
                    "options": ["🟩 Io ci sono per tutti e due! 🙋‍♀️", "🟥 Io passo"]
                }
            ]
            scelta = random.choice(varianti_doppie)
            question = scelta["question"]
            options = scelta["options"]
            
        else:
            # SONDAGGI SINGOLI (Comandi normali)
            varianti_singole = [
                {
                    "question": f"🚀 BOOST ARTICOLO DELLE {formatted_time} ❤️\n\nPartecipi al boost di adesso? Clicca sotto! 👇",
                    "options": ["🟩 Sì, ci sono e partecipo! 💯", "🟥 No, salto questo turno"]
                },
                {
                    "question": f"⏰ ORE {formatted_time} ➡️ BOOST ARTICOLO ❤️\n\nVota sotto se ci sei adesso: 👇",
                    "options": ["🟩 CI SONO! 🔥", "🟥 NON CI SONO ❌"]
                },
                {
                    "question": f"👋 Ragazzi, è l'ora del BOOST! (Ore {formatted_time}) ❤️\n\nChi è attivo e vuole spingere il proprio articolo? 👇",
                    "options": ["🟩 Io sono attivo! 🙋‍♀️", "🟥 Io non riesco ora"]
                }
            ]
            scelta = random.choice(varianti_singole)
            question = scelta["question"]
            options = scelta["options"]
        
        # Invia il sondaggio configurato
        await context.bot.send_poll(
            chat_id=update.effective_chat.id,
            question=question,
            options=options,
            is_anonymous=anonimo
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
    
    # Aggiornato il filtro per catturare opzionalmente anche le lettere d, D, i, I alla fine
    time_filter = filters.Regex(r"^/(h)?\d{1,4}[dDiI]?$")
    app.add_handler(MessageHandler(time_filter, handle_time_poll))

    print("Bot avviato con successo in modalita Polling!")
    app.run_polling()

if __name__ == '__main__':
    main()
