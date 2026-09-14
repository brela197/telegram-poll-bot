import os
import threading
import random
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone

# Fuso orario italiano per evitare sfasamenti con i server americani
ROMA_TZ = timezone('Europe/Rome')

# 1. SERVER WEB PER IMPEDIRE LO SLEEP DI RENDER (Gestisce GET e HEAD)
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"<html><body><h1>Bot is actively running!</h1></body></html>")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

def run_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# 2. FUNZIONAMENTO PER L'INVIO AUTOMATICO E IL FISSAGGIO (PIN) DEL SONDAGGIO
async def invia_sondaggio_automatico(app, orario_boost):
    # Recupera l'ID del gruppo dalle impostazioni di Render
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not chat_id:
        print("Errore: TELEGRAM_CHAT_ID non configurato nelle variabili d'ambiente!")
        return

    # Grafiche casuali (Tutte per ARTICOLO NORMALE)
    varianti_singole = [
        {
            "question": f"🚀 BOOST ARTICOLO DELLE {orario_boost} ❤️\n\nPartecipi al boost di adesso? Clicca sotto! 👇",
            "options": ["🟩 Sì, ci sono e partecipo! 💯", "🟥 No, salto questo turno"]
        },
        {
            "question": f"⏰ ORE {orario_boost} ➡️ BOOST ARTICOLO ❤️\n\nVota sotto se ci sei adesso: 👇",
            "options": ["🟩 CI SONO! 🔥", "🟥 NON CI SONO ❌"]
        },
        {
            "question": f"👋 Ragazzi, è l'ora del BOOST! (Ore {orario_boost}) ❤️\n\nChi è attivo e vuole spingere il proprio articolo? 👇",
            "options": ["🟩 Io sono attivo! 🙋‍♀️", "🟥 Io non riesco ora"]
        }
    ]
    scelta = random.choice(varianti_singole)

    try:
        # Invia il sondaggio nel gruppo
        poll_message = await app.bot.send_poll(
            chat_id=chat_id,
            question=scelta["question"],
            options=scelta["options"],
            is_anonymous=False
        )
        # AUTOMATISMO: Fissa il sondaggio in alto nel gruppo in modo silenzioso
        await app.bot.pin_chat_message(
            chat_id=chat_id,
            message_id=poll_message.message_id,
            disable_notification=True
        )
        print(f"Sondaggio automatico delle {orario_boost} inviato e fissato in alto!")
    except Exception as e:
        print(f"Errore nell'invio/fissaggio automatico: {e}")

# Funzione ponte per far dialogare il pianificatore con Telegram
def pianifica_task(app, orario_boost):
    app.loop.create_task(invia_sondaggio_automatico(app, orario_boost))

# 3. GESTIONE DEI COMANDI MANUALI (Attivi 7 giorni su 7)
async def start(update, context):
    await update.message.reply_text("Ciao! Il bot è attivo sia con i sondaggi automatici (Lun-Ven) che con i comandi manuali (Sempre).")

async def handle_time_poll(update, context):
    try:
        raw_text = update.message.text.strip().upper()
        is_info = raw_text.endswith('I')
        is_a4 = raw_text.endswith('A4')
        is_a6 = raw_text.endswith('A6')
        is_a10 = raw_text.endswith('A10')
        is_double = raw_text.endswith('D') and not (is_a4 or is_a6 or is_a10 or is_info)
        
        time_str = raw_text.replace("/H", "").replace("/", "")
        for suffix in ["A10", "A4", "A6", "D", "I"]:
            time_str = time_str.replace(suffix, "")
        
        if len(time_str) <= 2:
            formatted_time = f"{time_str.zfill(2)}:00"
        elif len(time_str) == 3:
            formatted_time = f"0{time_str}:{time_str[1:]}"
        elif len(time_str) == 4:
            formatted_time = f"{time_str[:2]}:{time_str[2:]}"
        else:
            formatted_time = time_str

        anonimo = False
        if is_info:
            anonimo = True
            question = f"⏰ {formatted_time} 👉 BOOST ARTICOLO ❤️ CON MESSAGGIO INFO 📩\n\n⚠️ Accessibile solo a 10 link max ⚠️\nInviare messaggi reali all'articolo/no emoticon 🚨"
            options = ["Yesss ❤️💌", "✖️"]
        elif is_a4:
            question = f"⏰ {formatted_time} 👉 🚀BOOST ARMADIO 🚪X4 ❤️\n\nSi pubblica il link armadio Vinted, si ricambia con 4 LIKE ❤️ ogni armadio pubblicato."
            options = ["🟩 Ci sono! 💯", "🟥 No, salto questo turno"]
        elif is_a6:
            question = f"⏰ {formatted_time} 👉 🚀BOOST ARMADIO 🚪X6 ❤️\n\nSi pubblica il link armadio Vinted, si ricambia con 6 LIKE ❤️ ogni armadio pubblicato."
            options = ["🟩 Ci sono! 💯", "🟥 No, salto questo turno"]
        elif is_a10:
            question = f"⏰ {formatted_time} 👉 🚀BOOST ARMADIO 🚪X10 ❤️\n\nSi pubblica il link armadio Vinted, si ricambia con 10 LIKE ❤️ ogni armadio pubblicato."
            options = ["🟩 Ci sono! 💯", "🟥 No, salto questo turno"]
        elif is_double:
            varianti_doppie = [
                {"question": f"🚀 DOPPIO BOOST DELLE {formatted_time} 💖💖\n\nPartecipi al doppio boost di adesso? Clicca sotto! 👇", "options": ["🟩 Sì, partecipo a entrambi! 💯", "🟥 No, salto questo turno"]},
                {"question": f"⏰ ORE {formatted_time} ➡️ DOPPIO BOOST 💖💖\n\nVota sotto se ci sei adesso: 👇", "options": ["🟩 CI SONO PER ENTRAMBI! 🔥", "🟥 NON CI SONO ❌"]},
                {"question": f"👋 Ragazzi, c'è il DOPPIO BOOST! (Ore {formatted_time}) 💖💖\n\nChi vuole fare doppietta di visualizzazioni adesso? 👇", "options": ["🟩 Io ci sono per tutti e due! 🙋‍♀️", "🟥 Io passo"]}
            ]
            scelta = random.choice(varianti_doppie)
            question, options = scelta["question"], scelta["options"]
        else:
            varianti_singole = [
                {"question": f"🚀 BOOST ARTICOLO DELLE {formatted_time} ❤️\n\nPartecipi al boost di adesso? Clicca sotto! 👇", "options": ["🟩 Sì, ci sono e partecipo! 💯", "🟥 No, salto questo turno"]},
                {"question": f"⏰ ORE {formatted_time} ➡️ BOOST ARTICOLO ❤️\n\nVota sotto se ci sei adesso: 👇", "options": ["🟩 CI SONO! 🔥", "🟥 NON CI SONO ❌"]},
                {"question": f"👋 Ragazzi, è l'ora del BOOST! (Ore {formatted_time}) ❤️\n\nChi è attivo e vuole spingere il proprio articolo? 👇", "options": ["🟩 Io sono attivo! 🙋‍♀️", "🟥 Io non riesco ora"]}
            ]
            scelta = random.choice(varianti_singole)
            question, options = scelta["question"], scelta["options"]

        await context.bot.send_poll(chat_id=update.effective_chat.id, question=question, options=options, is_anonymous=anonimo)
    except Exception as e:
        print(f"Errore comando manuale: {e}")

# 4. FUNZIONE PRINCIPALE ED ELENCO DEGLI ORARI PROGRAMMATI (LUN-VEN)
def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Errore: TELEGRAM_BOT_TOKEN non trovato!")
        return

    threading.Thread(target=run_server, daemon=True).start()

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    time_filter = filters.Regex(r"^/(h)?\d{1,4}([dDiI]|(A4)|(A6)|(A10))?$")
    app.add_handler(MessageHandler(time_filter, handle_time_poll))

    # Configurazione del programmatore automatico
    scheduler = BackgroundScheduler(timezone=ROMA_TZ)
    
    # Orari di invio impostati esattamente 20 minuti prima del boost reale
    orari_automatici = [
        {"ora": 7, "minuto": 40, "label": "08:00"},
        {"ora": 9, "minuto": 40, "label": "10:00"},
        {"ora": 12, "minuto": 40, "label": "13:00"},
        {"ora": 13, "minuto": 40, "label": "14:00"},
        {"ora": 14, "minuto": 40, "label": "15:00"},
        {"ora": 17, "minuto": 40, "label": "18:00"},
        {"ora": 18, "minuto": 40, "label": "19:00"},
        {"ora": 19, "minuto": 40, "label": "20:00"},
        {"ora": 20, "minuto": 40, "label": "21:00"},
        {"ora": 21, "minuto": 40, "label": "22:00"},
        {"ora": 22, "minuto": 40, "label": "23:00"}
    ]
    
    # Il parametro day_of_week='mon-fri' blocca l'esecuzione nel weekend
    for t in orari_automatici:
        scheduler.add_job(
            pianifica_task,
            'cron',
            day_of_week='mon-fri',
            hour=t["ora"],
            minute=t["minuto"],
            args=[app, t["label"]]
        )
    
    scheduler.start()
    print("Programmatore dei turni fissi avviato (attivo solo Lun-Ven)!")
    app.run_polling()

if __name__ == '__main__':
    main()
