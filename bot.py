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
        "Ciao! Il bot è attivo con tutte le opzioni grafiche.\n\n"
        "• `/8` o `/730` per sondaggio Singolo (Random)\n"
        "• `/8D` o `/730D` per sondaggio Doppio (Random)\n"
        "• `/8I` o `/730I` per sondaggio Anonimo Con Messaggio Info ✉️\n"
        "• `/8A4` o `/730A4` per sondaggio Boost Armadio X4 🚪\n"
        "• `/8A6` o `/730A6` per sondaggio Boost Armadio X6 🚪\n"
        "• `/8A10` o `/730A10` per sondaggio Boost Armadio X10 🚪"
    )

async def handle_time_poll(update, context):
    try:
        raw_text = update.message.text.strip().upper()
        
        # Identificazione del tipo di sondaggio in base a come termina il comando
        is_info = raw_text.endswith('I')
        is_a4 = raw_text.endswith('A4')
        is_a6 = raw_text.endswith('A6')
        is_a10 = raw_text.endswith('A10')
        is_double = raw_text.endswith('D') and not (is_a4 or is_a6 or is_a10 or is_info)
        
        # Pulizia della stringa per estrarre solo l'orario numerico
        time_str = raw_text.replace("/H", "").replace("/", "")
        for suffix in ["A10", "A4", "A6", "D", "I"]:
            time_str = time_str.replace(suffix, "")
        
        # Formattazione dell'orario
        if len(time_str) <= 2:
            formatted_time = f"{time_str.zfill(2)}:00"
        elif len(time_str) == 3:
            formatted_time = f"0{time_str}:{time_str[1:]}"
        elif len(time_str) == 4:
            formatted_time = f"{time_str[:2]}:{time_str[2:]}"
        else:
            formatted_time = time_str

        # Impostazioni di base del sondaggio
        question = ""
        options = ["🟩 Ci sono! 💯", "🟥 No, salto questo turno"]
        anonimo = False

        # LOGICA DI CONFIGURAZIONE DEL TESTO E DELLE OPZIONI
        if is_info:
            # SONDAGGIO ANONIMO CON MESSAGGIO INFO (Layout pulito e ordinato)
            anonimo = True
            question = (
                f"⏰ {formatted_time} 👉 BOOST ARTICOLO ❤️ CON MESSAGGIO INFO 📩\n\n"
                f"⚠️ Accessibile solo a 10 link max ⚠️\n"
                f"Inviare messaggi reali all'articolo/no emoticon 🚨"
            )
            options = ["Yesss 🍊🍊🍊", "✖️"]
            
        elif is_a4:
            # 🚪 BOOST ARMADIO X4
            question = (
                f"⏰ {formatted_time} 👉 🚀BOOST ARMADIO 🚪X4 ❤️\n\n"
                f"Si pubblica il link armadio Vinted, si ricambia con 4 LIKE ❤️ ogni armadio pubblicato."
            )
            
        elif is_a6:
            # 🚪 BOOST ARMADIO X6
            question = (
                f"⏰ {formatted_time} 👉 🚀BOOST ARMADIO 🚪X6 ❤️\n\n"
                f"Si pubblica il link armadio Vinted, si ricambia con 6 LIKE ❤️ ogni armadio pubblicato."
            )
            
        elif is_a10:
            # 🚪 BOOST ARMADIO X10
            question = (
                f"⏰ {formatted_time} 👉 🚀BOOST ARMADIO 🚪X10 ❤️\n\n"
                f"Si pubblica il link armadio Vinted, si ricambia con 10 LIKE ❤️ ogni armadio pubblicato."
            )
            
        elif is_double:
            # SONDAGGI DOPPI (Casuali - Vecchia logica mantenuta)
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
            # SONDAGGI SINGOLI (Casuali - Vecchia logica mantenuta)
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
        
        # Invio definitivo del sondaggio configurato
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
    
    # Filtro Regex corretto senza l'opzione invalida
    time_filter = filters.Regex(r"^/(h)?\d{1,4}([dDiI]|(A4)|(A6)|(A10))?$")
    app.add_handler(MessageHandler(time_filter, handle_time_poll))

    print("Bot avviato con successo in modalita Polling!")
    app.run_polling()

if __name__ == '__main__':
    main()
