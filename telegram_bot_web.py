import os
from flask import Flask, request
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from email_manager import run_email_summarization


load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("t_bot_token")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Should be: https://your-app.onrender.com/webhook

# Flask app for Render
app = Flask(__name__)

# Build Telegram bot application (required for webhook mode)
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()


# -------------------------
#  HANDLERS
# -------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! Send /summarize to process and summarize your latest emails."
    )

async def summarize_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Starting summarization...")

    result = run_email_summarization()
    print("from telegram bot ", result)

    await update.message.reply_text(result)
    await update.message.reply_text(
        "Here's the G-sheet link:\n https://docs.google.com/spreadsheets/d/1X-ZDU-DWwKbk3OoVqzdDV6BIJqtTwHBCTVKED_FipUE/edit?usp=sharing"
    )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip().lower()
    if "summarize" in text:
        return await summarize_cmd(update, context)


# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("summarize", summarize_cmd))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))


# -------------------------
#  WEBHOOK ENDPOINT
# -------------------------
@app.post("/webhook")
def webhook():
    """Receives updates from Telegram"""
    data = request.get_json()
    if data:
        update = Update.de_json(data, application.bot)
        application.create_task(application.process_update(update))

    return "OK", 200


# -------------------------
#  WEBHOOK SETUP ENDPOINT
# -------------------------
@app.get("/set_webhook")
async def set_webhook():
    """Call this once after deployment"""
    await application.bot.set_webhook(WEBHOOK_URL)
    return "Webhook set!", 200


# -------------------------
#  APP ENTRYPOINT
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6000))
    print(f"Starting Flask server on port {port}...")
    app.run(host="0.0.0.0", port=port)