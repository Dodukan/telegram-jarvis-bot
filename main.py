from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os, requests, asyncio
from google import genai

TOKEN = os.getenv("TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
WEATHER_KEY = os.getenv("WEATHER_KEY")
CHAT_ID = os.getenv("CHAT_ID")

client = genai.Client(api_key=GOOGLE_API_KEY)
scheduler = AsyncIOScheduler()
reminders = {}

# === GEMİNİ CEVAP ===
def ask_gemini(prompt):
    response = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
    return response.text

# === KOMUTLAR ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Merhaba! Ben Jarvis!\n\n"
        "Komutlar:\n"
        "/hava [şehir] → Hava durumu\n"
        "/hatırlat [dakika] [mesaj] → Hatırlatıcı\n"
        "/özet [metin] → Metin özetle\n"
        "/çevir [dil] [metin] → Çeviri\n\n"
        "Fotoğraf veya sesli mesaj da gönderebilirsin!"
    )

async def hava(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Kullanım: /hava Istanbul")
        return
    sehir = " ".join(context.args)
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={sehir}&appid={WEATHER_KEY}&units=metric&lang=tr"
        r = requests.get(url).json()
        mesaj = (
            f"🌤 {r['name']} Hava Durumu:\n"
            f"🌡 Sıcaklık: {r['main']['temp']}°C\n"
            f"💧 Nem: {r['main']['humidity']}%\n"
            f"🌬 Rüzgar: {r['wind']['speed']} m/s\n"
            f"☁️ Durum: {r['weather'][0]['description']}"
        )
        await update.message.reply_text(mesaj)
    except:
        await update.message.reply_text("❌ Şehir bulunamadı!")

async def ozet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Kullanım: /özet [metin]")
        return
    metin = " ".join(context.args)
    cevap = ask_gemini(f"Bu metni kısaca özetle: {metin}")
    await update.message.reply_text(f"📝 Özet:\n{cevap}")

async def cevir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Kullanım: /çevir ingilizce merhaba")
        return
    dil = context.args[0]
    metin = " ".join(context.args[1:])
    cevap = ask_gemini(f"Şunu {dil} diline çevir, sadece çeviriyi yaz: {metin}")
    await update.message.reply_text(f"🌐 Çeviri:\n{cevap}")

async def hatirla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Kullanım: /hatırlat 30 toplantı var")
        return
    try:
        dakika = int(context.args[0])
        mesaj = " ".join(context.args[1:])
        chat_id = update.message.chat_id
        
        async def gonder():
            await context.bot.send_message(chat_id=chat_id, text=f"⏰ Hatırlatma: {mesaj}")
        
        scheduler.add_job(gonder, 'interval', minutes=dakika, max_instances=1, id=str(chat_id))
        await update.message.reply_text(f"✅ {dakika} dakika sonra hatırlatacağım: {mesaj}")
    except:
        await update.message.reply_text("❌ Hata! Kullanım: /hatırlat 30 toplantı var")

# === MESAJ ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        cevap = ask_gemini(user_message)
        await update.message.reply_text(cevap)
    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {str(e)}")

# === SESLİ MESAJ ===
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎤 Sesli mesaj aldım! Şu an ses tanıma geliştiriliyor, yazarak sor!")

# === FOTOĞRAF ===
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo = update.message.photo[-1]
        file = await photo.get_file()
        file_path = "photo.jpg"
        await file.download_to_drive(file_path)
        
        import PIL.Image
        img = PIL.Image.open(file_path)
        
        caption = update.message.caption or "Bu fotoğrafı analiz et ve ne olduğunu açıkla"
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[caption, img]
        )
        await update.message.reply_text(f"🖼 Analiz:\n{response.text}")
    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {str(e)}")

# === SABAH HABERLERİ ===
async def sabah_haberleri(bot):
    if CHAT_ID:
        haber = ask_gemini("Bugün için motivasyonel bir günaydın mesajı ve 3 önemli gündem maddesi yaz (Türkçe)")
        await bot.send_message(chat_id=CHAT_ID, text=f"🌅 Günaydın!\n\n{haber}")

# === ANA FONKSİYON ===
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hava", hava))
    app.add_handler(CommandHandler("ozet", ozet))
    app.add_handler(CommandHandler("cevir", cevir))
    app.add_handler(CommandHandler("hatirla", hatirla))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Sabah 08:00 haberleri
    scheduler.add_job(
        lambda: asyncio.create_task(sabah_haberleri(app.bot)),
        'cron', hour=8, minute=0
    )
    scheduler.start()
    
    print("✅ Jarvis başlatıldı!")
    app.run_polling()
