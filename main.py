import os
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Dummy Web Server per Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

async def gestisci_messaggio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    testo = update.message.text.strip().lower()
    match = re.match(r'^/h([0-9]|1[0-9]|2[0-3])([0-5][0-9])?$', testo)
    if not match:
        return

    ora = match.group(1)
    minuti = match.group(2) if match.group(2) else "00"
    orario_str = f"{ora.zfill(2)}:{minuti}"

    try:
        await update.message.delete()
    except Exception:
        pass

    await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question=f"⏰ {orario_str} ➡️ BOOST ARTICOLO ❤️‍ Ci siete?",
        options=["🟩 Presente", "🟥 Assente"],
        is_anonymous=True
    )

token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
app = ApplicationBuilder().token(token).build()
app.add_handler(MessageHandler(filters.COMMAND, gestisci_messaggio))

print("Bot attivo!")
app.run_polling()
