import os
import threading
import random
import asyncio
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone

ROMA_TZ = timezone('Europe/Rome')

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

# FUNZIONE DELLE :39 (INVIA SONDAGGIO, PINNA E CHIUDE CHAT)
async def task_sondaggio_e_chiusura(app, orario_boost):
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not chat_id: return

    varianti_singole = [
        {"question": f"🚀 BOOST ARTICOLO DELLE {orario_boost} ❤️\n\nPartecipi al boost di adesso? Clicca sotto! 👇", "options": ["🟩 Sì, ci sono e partecipo! 💯", "🟥 No, salto questo turno"]},
        {"question": f"⏰ ORE {orario_boost} ➡️ BOOST ARTICOLO ❤️\n\nVota sotto se ci sei adesso: 👇", "options": ["🟩 CI SONO! 🔥", "🟥 NON CI SONO ❌"]},
        {"question": f"👋 Ragazzi, è l'ora del BOOST! (Ore {orario_boost}) ❤️\n\nChi è attivo e vuole spingere il proprio articolo? 👇", "options": ["🟩 Io sono attivo! 🙋‍♀️", "🟥 Io non riesco ora"]}
    ]
    scelta = random.choice(varianti_singole)

    try:
        poll_message = await app.bot.send_poll(chat_id=chat_id, question=scelta["question"], options=scelta["options"], is_anonymous=False)
        await app.bot.pin_chat_message(chat_id=chat_id, message_id=poll_message.message_id, disable_notification=True)
        
        permissions = ChatPermissions(can_send_messages=False)
        await app.bot.set_chat_permissions(chat_id=chat_id, permissions=permissions)
        print(f"Sondaggio delle {orario_boost} inviato e chat bloccata al minuto :39!")
    except Exception as e:
        print(f"Errore in fase di chiusura chat: {e}")

# FUNZIONE DELLE :59 (SBLOCCA LA CHAT PER LASCIARE SPAZIO A GROUPHELP)
async def task_apertura_chat(app, orario_boost):
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not chat_id: return

    try:
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_audios=True,
            can_send_documents=True,
            can_send_photos=True,
            can_send_videos=True,
            can_send_video_notes=True,
            can_send_voice_notes=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
        await app.bot.set_chat_permissions(chat_id=chat_id, permissions=permissions)
        print(f"Chat sbloccata con successo per il boost delle {orario_boost}!")
    except Exception as e:
        print(f"Errore in fase di apertura chat: {e}")

def ponte_chiusura(app, orario_boost):
    asyncio.run_coroutine_threadsafe(task_sondaggio_e_chiusura(app, orario_boost), app.loop)

def ponte_apertura(app, orario_boost):
    asyncio.run_coroutine_threadsafe(task_apertura_chat(app, orario_boost), app.loop)
# GESTIONE COMANDI MANUALI (Attivi per le emergenze)
async def start(update, context):
    await update.message.reply_text("Bot attivo in modalita Webhook con chiusura a :39 e sblocco a :59.")

async def handle_time_poll(update, context):
    try:
        raw_text = update.message.text.strip().upper()
        is_info = raw_text.endswith('I')
        is_a4 = raw_text.endswith('A4')
        is_a6 = raw_text.endswith('A6')
        is_a10 = raw_text.endswith('A10')
        is_double = raw_text.endswith('D') and not (is_a4 or is_a6 or is_a10 or is_info)
        
        time_str = raw_text.replace("/H", "").replace("/", "")
        for suffix in ["A10", "A4", "A6", "D", "I"]: time_str = time_str.replace(suffix, "")
        
        if len(time_str) <= 2: formatted_time = f"{time_str.zfill(2)}:00"
        elif len(time_str) == 3: formatted_time = f"0{time_str}:{time_str[1:]}"
        elif len(time_str) == 4: formatted_time = f"{time_str[:2]}:{time_str[2:]}"
        else: formatted_time = time_str

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

# PROGRAMMAZIONE AUTOMATICA LUN-VEN
def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token: return

    threading.Thread(target=run_server, daemon=True).start()

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    time_filter = filters.Regex(r"^/(h)?\d{1,4}([dDiI]|(A4)|(A6)|(A10))?$")
    app.add_handler(MessageHandler(time_filter, handle_time_poll))

    scheduler = BackgroundScheduler(timezone=ROMA_TZ)
    
    turni = [
        {"ora_boost": "08:00", "h_chiusura": 7, "m_chiusura": 39, "h_apertura": 7, "m_apertura": 59},
        {"ora_boost": "10:00", "h_chiusura": 9, "m_chiusura": 39, "h_apertura": 9, "m_apertura": 59},
        {"ora_boost": "13:00", "h_chiusura": 12, "m_chiusura": 39, "h_apertura": 12, "m_apertura": 59},
        {"ora_boost": "14:00", "h_chiusura": 13, "m_chiusura": 39, "h_apertura": 13, "m_apertura": 59},
        {"ora_boost": "15:00", "h_chiusura": 14, "m_chiusura": 39, "h_apertura": 14, "m_apertura": 59},
        {"ora_boost": "18:00", "h_chiusura": 17, "m_chiusura": 39, "h_apertura": 17, "m_apertura": 59},
        {"ora_boost": "19:00", "h_chiusura": 18, "m_chiusura": 39, "h_apertura": 18, "m_apertura": 59},
        {"ora_boost": "20:00", "h_chiusura": 19, "m_chiusura": 39, "h_apertura": 19, "m_apertura": 59},
        {"ora_boost": "21:00", "h_chiusura": 20, "m_chiusura": 39, "h_apertura": 20, "m_apertura": 59},
        {"ora_boost": "22:00", "h_chiusura": 21, "m_chiusura": 39, "h_apertura": 21, "m_apertura": 59},
        {"ora_boost": "23:00", "h_chiusura": 22, "m_chiusura": 39, "h_apertura": 22, "m_apertura": 59}
    ]
    
    for t in turni:
        scheduler.add_job(ponte_chiusura, 'cron', day_of_week='mon-fri', hour=t["h_chiusura"], minute=t["m_chiusura"], args=[app, t["ora_boost"]])
        scheduler.add_job(ponte_apertura, 'cron', day_of_week='mon-fri', hour=t["h_apertura"], minute=t["m_apertura"], args=[app, t["ora_boost"]])
    
    scheduler.start()
    print("Sistema di blocco chat avviato in modalita Webhook!")
    
    # AVVIO ASINCRONO IN WEBHOOK (Risolve il conflitto e libera la linea per l'altro bot)
    port = int(os.environ.get('PORT', 10000))
    render_url = os.environ.get("RENDER_EXTERNAL_URL", "https://onrender.com")
    
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=token,
        webhook_url=f"{render_url}/{token}"
    )

if __name__ == '__main__':
    main()
