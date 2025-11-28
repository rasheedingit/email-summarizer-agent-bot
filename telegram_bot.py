import os
from telegram import Update
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
# from telegram.ext import (
#     ApplicationBuilder,
#     CommandHandler,
#     MessageHandler,
#     ContextTypes,
#     filters
# )

from email_manager import run_email_summarization



TELEGRAM_BOT_TOKEN = os.getenv("t_bot_token")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! Send /summarize to process and summarize your latest emails."
    )

async def summarize_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Starting summarization...")

    # Run the workflow (sync) – if heavy, move to thread / async executor
    result = run_email_summarization()
    print("from telegram bot ",result)

    await update.message.reply_text(result)
    await update.message.reply_text("Here's the G-sheet link:\n https://docs.google.com/spreadsheets/d/1X-ZDU-DWwKbk3OoVqzdDV6BIJqtTwHBCTVKED_FipUE/edit?usp=sharing", )


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip().lower()
    if "summarize" in text:
        return await summarize_cmd(update, context)

def main():
    load_dotenv()
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("summarize", summarize_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    #app.stop()
    app.run_polling()

if __name__ == "__main__":
    main()