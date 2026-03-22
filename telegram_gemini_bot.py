import os
import tempfile
from groq import Groq
from gtts import gTTS
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = "8668267460:AAHWtFyxgUgsVcXRTXjVTrzBZyWIlAxGb2c"
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)
chat_histories = {}

def get_ai_response(user_id, user_message):
    if user_id not in chat_histories:
        chat_histories[user_id] = [{"role": "system", "content": "You are a helpful AI assistant. Always respond in the same language the user is using - Hindi or English."}]
    chat_histories[user_id].append({"role": "user", "content": user_message})
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=chat_histories[user_id]
    )
    ai_reply = response.choices[0].message.content
    chat_histories[user_id].append({"role": "assistant", "content": ai_reply})
    return ai_reply

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalam o Alaikum! 👋\nMain aapka AI Assistant hoon 🤖\n\nMain text aur voice dono samajhta hoon!\n\n/reset - Chat clear karo")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_histories[update.message.from_user.id] = []
    await update.message.reply_text("Chat clear ho gayi!")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_message = update.message.text
    await update.message.chat.send_action("typing")
    try:
        ai_reply = get_ai_response(user_id, user_message)
        await update.message.reply_text(ai_reply)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    await update.message.chat.send_action("typing")
    try:
        # Voice message download karo
        voice = update.message.voice
        voice_file = await context.bot.get_file(voice.file_id)
        
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            await voice_file.download_to_drive(tmp.name)
            tmp_path = tmp.name

        # Groq Whisper se voice to text
        with open(tmp_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file
            )
        user_message = transcription.text
        os.unlink(tmp_path)

        await update.message.reply_text(f"🎤 Aapne kaha: {user_message}")

        # AI se jawab lo
        ai_reply = get_ai_response(user_id, user_message)

        # Text jawab bhejo
        await update.message.reply_text(ai_reply)

        # Voice jawab banao
        await update.message.chat.send_action("record_voice")
        tts = gTTS(text=ai_reply, lang='hi' if any(ord(c) > 127 for c in ai_reply) else 'en')
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_audio:
            tts.save(tmp_audio.name)
            tmp_audio_path = tmp_audio.name

        with open(tmp_audio_path, "rb") as audio:
            await update.message.reply_voice(voice=audio)
        os.unlink(tmp_audio_path)

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

def main():
    print("Bot chal raha hai...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    print("Bot ready!")
    app.run_polling()

if __name__ == "__main__":
    main()
