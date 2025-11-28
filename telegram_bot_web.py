import os
import asyncio
from aiohttp import web
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from email_manager import run_email_summarization


load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("t_bot_token")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://your-app.onrender.com/webhook


# ----------------------------
# Telegram Bot Handlers
# ----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send /summarize to process emails.")

async def summarize_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Starting summarization...")
    result = run_email_summarization()
    await update.message.reply_text(result)
    await update.message.reply_text(
        "Here's the G-sheet link:\n"
        "https://docs.google.com/spreadsheets/d/1X-ZDU-DWwKbk3OoVqzdDV6BIJqtTwHBCTVKED_FipUE/edit?usp=sharing"
    )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "summarize" in update.message.text.lower():
        return await summarize_cmd(update, context)


# ----------------------------
# AIOHTTP Webhook Server
# ----------------------------
async def handle_webhook(request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return web.Response(text="OK")


async def set_webhook():
    await application.bot.set_webhook(WEBHOOK_URL)
    print("Webhook set!")


# ----------------------------
# Main Entry Point
# ----------------------------

async def main():
    global application

    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("summarize", summarize_cmd))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    # Start bot (asynchronously) – webhook only (no polling)
    await application.initialize()
    await application.start()
    await set_webhook()

    # AIOHTTP server
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)

    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Server running on port {port}…")

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    # Keep running forever
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())