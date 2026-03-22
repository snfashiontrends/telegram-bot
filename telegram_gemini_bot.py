from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = "8668267460:AAHWtFyxgUgsVcXRTXjVTrzBZyWIlAxGb2c"
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)
chat_histories = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalam o Alaikum! 👋\nMain aapka AI Assistant hoon 🤖\nKoi bhi sawaal poochein!\n/reset - Chat clear karo")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_histories[update.message.from_user.id] = []
    await update.message.reply_text("Chat clear ho gayi!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_message = update.message.text
    await update.message.chat.send_action("typing")
    if user_id not in chat_histories:
        chat_histories[user_id] = [{"role": "system", "content": "Aap ek helpful AI assistant hain. Urdu aur Hindi mein baat kar sakte hain."}]
    chat_histories[user_id].append({"role": "user", "content": user_message})
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=chat_histories[user_id]
        )
        ai_reply = response.choices[0].message.content
        chat_histories[user_id].append({"role": "assistant", "content": ai_reply})
        await update.message.reply_text(ai_reply)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

def main():
    print("Bot chal raha hai...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot ready!")
    app.run_polling()

if __name__ == "__main__":
    main()
