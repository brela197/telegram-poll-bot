import os
import threading
import random
import asyncio
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
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

# 1. FUNZIONE AUTOMATICA :39 (TURNO FISSO ISTITUZIONALE + BLOCCO CHAT)
async def task_sondaggio_e_chiusura(app, orario_boost):
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not chat_id: return

    question = f"⏰ {orario_boost} 👉🏻 BOOST ARTICOLO ❤️"
    options = ["🟩 Sì, ci sono e partecipo! 💯", "🟥 No, salto questo turno"]

    try:
        poll_message = await app.bot.send_poll(chat_id=chat_id, question=question, options=options, is_anonymous=False)
        await app.bot.pin_chat_message(chat_id=chat_id, message_id=poll_message.message_id, disable_notification=True)
        
        # BLOCCO CHAT: Disattiva la scrittura per i membri semplici
        permissions = ChatPermissions(can_send_messages=False)
        await app.bot.set_chat_permissions(chat_id=chat_id, permissions=permissions)
        print(f"Turno Fisso delle {orario_boost} inviato e chat bloccata!")
    except Exception as e:
        print(f"Errore in fase di chiusura chat: {e}")

# 2. FUNZIONE AUTOMATICA :59 (SBLOCCO CHAT PERSONALIZZATO SULLA TUA FOTO)
async def task_apertura_chat(app, orario_boost):
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not chat_id: return

    try:
        # SBLOCCO MIRATO: Attiva SOLO i permessi che si vedono accesi nel tuo screenshot
        permissions = ChatPermissions(
            can_send_messages=True,       # Inviare messaggi di testo 🔵
            can_send_videos=True,         # Video 🔵
            can_send_voice_notes=True,     # Messaggi vocali 🔵
            can_send_other_messages=True,  # Inviare reazioni 🔵
            can_send_photos=False,         # Foto ⚪ (Disattivato)
            can_send_audios=False,         # Musica ⚪ (Disattivato)
            can_send_documents=False,      # File ⚪ (Disattivato)
            can_send_video_notes=False,    # Videomessaggi ⚪ (Disattivato)
            can_send_polls=False,          # Sondaggi ⚪ (Disattivato)
            can_add_web_page_previews=False # Link con anteprima ⚪ (Disattivato)
        )
        await app.bot.set_chat_permissions(chat_id=chat_id, permissions=permissions)
        print(f"Chat sbloccata ripristinando i permessi standard del gruppo per le {orario_boost}!")
    except Exception as e:
        print(f"Errore in fase di apertura chat: {e}")

# 3. GESTIONE COMANDI MANUALI ADMIN (GRAFICHE FLASH CASUALI)
async def start(update, context):
    await update.message.reply_text("Bot attivo. Turni fissi automatici (Lun-Ven) e Turni Flash manuali attivi.")

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
        
        if len(time_str) <= 2: formatted_time = f"{time_str.zfill(2)}:00"
        elif len(time_str) == 3: formatted_time = f"0{time_str}:{time_str[1:]}"
        elif len(time_str) == 4: formatted_time = f"{time_str[:2]}:{time_str[2:]}"
        else: formatted_time = time_str

        anonimo = False
        options = ["🟩 Ci sono! 💯", "🟥 No, salto questo turno"]

        if is_info:
            anonimo = True
            question = f"⏰ {formatted_time} 👉 BOOST ARTICOLO ❤️ CON MESSAGGIO INFO 📩\n\n⚠️ Accessibile solo a 10 link max ⚠️\nInviare messaggi reali all'articolo/no emoticon 🚨"
            options = ["Yesss ❤️💌", "✖️"]
        elif is_a4:
            question = f"⏰ {formatted_time} 👉 🚀BOOST ARMADIO 🚪X4 ❤️\n\nSi pubblica il link armadio Vinted, si ricambia con 4 LIKE ❤️ ogni armadio pubblicato."
        elif is_a6:
            question = f"⏰ {formatted_time} 👉 🚀BOOST ARMADIO 🚪X6 ❤️\n\nSi pubblica il link armadio Vinted, si ricambia con 6 LIKE ❤️ ogni armadio pubblicato."
        elif is_a10:
            question = f"⏰ {formatted_time} 👉 🚀BOOST ARMADIO 🚪X10 ❤️\n\nSi pubblica il link armadio Vinted, si ricambia con 10 LIKE ❤️ ogni armadio pubblicato."
        elif is_double:
            varianti_doppie_flash = [
                f"⏱️ {formatted_time} 🎯 BOOST ARTICOLO DOPPIO FLASH ⚡\n\nDoppia giocata rapida! Vuoi partecipare adesso? 👇",
                f"⏱️ {formatted_time} 🎯 BOOST ARTICOLO DOPPIO FLASH ⚡\n\nCarichi per la doppietta extra? Ci sei? 👇",
                f"⏱️ {formatted_time} 🎯 BOOST ARTICOLO DOPPIO FLASH ⚡\n\nSpingiamo questi due post al volo! Sei attiva? 👇"
            ]
            question = random.choice(varianti_doppie_flash)
            options = ["🟩 CI SONO PER ENTRAMBI! 🔥", "🟥 NON CI SONO ❌"]
        else:
            varianti_singole_flash = [
                f"⏱️ {formatted_time} 🎯 BOOST ARTICOLO FLASH ⚡\n\nGiocata extra veloce! Vuoi partecipare? 👇",
                f"⏱️ {formatted_time} 🎯 BOOST ARTICOLO FLASH ⚡\n\nUnisciti al volo al boost rapido! Ci sei? 👇",
                f"⏱️ {formatted_time} 🎯 BOOST ARTICOLO FLASH ⚡\n\nChi è attiva in chat adesso per spingere il post? Clicca sotto! 👇"
            ]
            question = random.choice(varianti_singole_flash)

        await context.bot.send_poll(update.effective_chat.id, question=question, options=options, is_anonymous=anonimo)
    except Exception as e:
        print(f"Errore comando manuale: {e}")

# 4. PROGRAMMAZIONE AUTOMATICA LUN-VEN
def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token: return

    threading.Thread(target=run_server, daemon=True).start()

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    time_filter = filters.Regex(r"(?i)^/(h)?\d{1,4}([dDiI]|(A4)|(A6)|(A10))?$")
    app.add_handler(MessageHandler(time_filter, handle_time_poll))

    scheduler = AsyncIOScheduler(timezone=ROMA_TZ)
    
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
        scheduler.add_job(task_sondaggio_e_chiusura, 'cron', day_of_week='mon-fri', hour=t["h_chiusura"], minute=t["m_chiusura"], args=[app, t["ora_boost"]])
        scheduler.add_job(task_apertura_chat, 'cron', day_of_week='mon-fri', hour=t["h_apertura"], minute=t["m_apertura"], args=[app, t["ora_boost"]])
    
    scheduler.start()
    print("Sistema avviato con sblocco permessi personalizzato!")
    app.run_polling(close_loop=False)

if __name__ == '__main__':
    main()
    
