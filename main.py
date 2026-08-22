from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os

TOKEN = os.getenv("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Merhaba! Ben Jarvis!\n\nMetin yaz veya sesli mesaj gönder!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.lower()
    
    # Basit akıllı cevaplar
    if "merhaba" in user_message:
        await update.message.reply_text("Selam! Nasıl yardımcı olabilirim?")
    elif "saat kaç" in user_message:
        await update.message.reply_text("⏰ Saat bilgisi için cihazını kontrol et!")
    elif "kim sin" in user_message:
        await update.message.reply_text("Ben Jarvis, senin yapay zeka asistanın!")
    elif "ne yap" in user_message:
        await update.message.reply_text("📱 Soruların cevapla, mesajları yönet, bilgiler ver!")
    else:
        await update.message.reply_text(f"✅ Anladım: {user_message}")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎤 Sesli mesaj aldım! (Özellik geliştiriliyor)")

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))  # Sesli mesaj
    app.run_polling()
