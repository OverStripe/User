from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests

BOT_TOKEN = "7371066438:AAFWQ5Ow_6gBq4DxurEnSVQcZTgMBZa13Bg"

# Function to check a single username
def check_username(username):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/checkUsername"
    payload = {"username": username}
    response = requests.post(url, json=payload)
    return response.json().get("ok", False)

# Command to check bulk usernames sent as multiline input
async def check_bulk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Extract usernames from the message (sent as multiple lines)
    usernames = update.message.text.splitlines()[1:]  # Skip the command line (/checkbulk)

    if not usernames:
        await update.message.reply_text("Please provide a list of usernames, each on a new line.")
        return

    results = []
    for username in usernames:
        username = username.strip()  # Clean up whitespace
        if len(username) < 5 or len(username) > 32:
            results.append(f"{username}: Invalid (length must be 5-32 characters)")
        else:
            available = check_username(username)
            if available:
                results.append(f"{username}: Available ✅")
            else:
                results.append(f"{username}: Not Available ❌")

    await update.message.reply_text("\n".join(results))

# Main function to set up the bot
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add the bulk username checker handler
    application.add_handler(CommandHandler("checkbulk", check_bulk))

    # Start the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
