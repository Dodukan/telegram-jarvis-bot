import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os

TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Merhaba! Ben Jarvis, senin asistanın!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.lower()
    
    if "merhaba" in user_message:
        await update.message.reply_text("Selam! Nasıl yardımcı olabilirim?")
    elif "kim sin" in user_message:
        await update.message.reply_text("Ben Jarvis, yapay zeka asistanınız!")
    else:
        await update.message.reply_text(f"Anladım: {update.message.text}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot başlatıldı!")
    app.run_polling()

if __name__ == '__main__':
    main()
