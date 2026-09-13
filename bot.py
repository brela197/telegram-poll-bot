import logging, re
from telegram import Update
from telegram.ext import (
    Application, CommandHandler,
    ContextTypes, MessageHandler, filters
)

TOKEN_SONDAGGI = "8190766468:AAFlZco9w7v9uK_U6U_N3eF9Yv1_Vlw8Wuo"
ID_GRUPPO_TARGET = -1001993054666

logging.basicConfig(level=logging.INFO)

async def gestisci_comando_orario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.id != ID_GRUPPO_TARGET: return
    txt = update.message.text if update.message else ""
    if not txt: return
    
    match = re.search(r'/?h?(\d{3,4})', txt.lower())
    if not match: return
    
    cifre = match.group(1)
    if len(cifre) == 3: cifre = "0" + cifre
    
    ora_pulita = f"{cifre[:2]}:{cifre[2:]}"
    titolo = f"👋 Ragazzi, è l'ora del BOOST! (Ore {ora_pulita}) ❤️"
    opzioni = ["🟩 Io sono attivo! 🙋‍♀️", "🟥 Io non riesco ora 🤷‍♀️"]    try:
        await context.bot.send_poll(
            chat_id=ID_GRUPPO_TARGET,
            question=titolo,
            options=opzioni,
            is_anonymous=False,
            allows_multiple_answers=False
        )
        await update.message.delete()
    except Exception as e:
        logging.error(f"Errore invio sondaggio: {e}")

def main():
    app = Application.builder().token(TOKEN_SONDAGGI).build()
    app.add_handler(CommandHandler(re.compile(r'^h\d+$'), gestisci_comando_orario))
    app.add_handler(MessageHandler(filters.Regex(r'^/?h?\d+$'), gestisci_comando_orario))
    logging.info("Bot dei sondaggi avviato con successo su Render!")
    app.run_polling(drop_pending_updates=True)

main()

