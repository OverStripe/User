import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackContext,
)

# Telegram Bot Token
TOKEN = '7617781212:AAEv2T8xETBqh04wiCsle1ubCG136CnXDaE'

# API Endpoints for Username Availability
TELEGRAM_API_URL = "https://t.me/"
FRAGMENT_API_URL = "https://fragment.com/username/"

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "✅ **Welcome to the Username Checker Bot!**\n\n"
        "🔹 To check usernames, use:\n`/check username1 username2 username3`\n"
        "🔹 To stop the bot, use:\n`/stop`"
    )

# Check Usernames Command
async def check_usernames(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "⚠️ Please provide a list of usernames separated by spaces.\n"
            "Example: `/check ecaru ecar0 ecarv`"
        )
        return

    usernames = [username.strip() for username in context.args]
    response_text = ""

    for username in usernames:
        try:
            # Check on Telegram
            tg_response = requests.get(f"{TELEGRAM_API_URL}{username}")
            telegram_status = "✅ Available" if tg_response.status_code == 404 else "❌ Taken"

            # Check on Fragment
            frag_response = requests.get(f"{FRAGMENT_API_URL}{username}")
            fragment_status = "✅ Available" if frag_response.status_code == 404 else "❌ Taken"

            response_text += f"🔹 **Username:** @{username}\n"
            response_text += f"   🟢 Telegram: {telegram_status}\n"
            response_text += f"   🟠 Fragment: {fragment_status}\n\n"

        except requests.RequestException as e:
            response_text += f"⚠️ Error checking @{username}: {str(e)}\n\n"

    await update.message.reply_text(response_text if response_text else "No valid usernames provided.")

# Stop Command
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("👋 **Bot is shutting down. Goodbye!**")
    await context.application.stop()
    print("Bot stopped by user command.")

# Main Function
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('check', check_usernames))
    app.add_handler(CommandHandler('stop', stop))

    print("✅ Bot is running... Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == '__main__':
    main()
