from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random
import aiohttp
import nltk
from nltk.corpus import words

# Your Telegram bot token
BOT_TOKEN = "7371066438:AAEEovTNkirmOkikBfgvi_NIHFSVUQSq8hw"

# Ensure the NLTK word list is downloaded
nltk.download("words")
WORD_LIST = words.words()

# Generate short meaningful words (5-12 characters)
SHORT_WORD_LIST = [word for word in WORD_LIST if 5 <= len(word) <= 12 and word.isalpha()]

# Check username availability using Telegram's API
async def check_username(username: str) -> bool:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat"
    payload = {"chat_id": f"@{username}"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            data = await response.json()
            return not data.get("ok", False)  # True if the username is available

# Generate random meaningful words
def generate_random_words(count=10) -> list:
    return random.sample(SHORT_WORD_LIST, count)

# Generate meaningful variations for a word
def generate_variations(word: str) -> list:
    return [
        word,
        f"{word}s",
        f"{word}ing",
        f"{word}ly",
        f"the{word}",
        f"my{word}",
    ]

# Command: Generate and check usernames
async def generate_usernames(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Generating usernames...")

    # Step 1: Generate random words
    random_words = generate_random_words(10)
    await update.message.reply_text(f"Generated words: {', '.join(random_words)}")

    available_usernames = []

    # Step 2: Check single words first
    for word in random_words:
        if await check_username(word):
            available_usernames.append(word)
        if len(available_usernames) >= 5:
            break

    # Step 3: If fewer than 5 usernames, try variations
    if len(available_usernames) < 5:
        for word in random_words:
            for variation in generate_variations(word):
                if await check_username(variation):
                    available_usernames.append(variation)
                    if len(available_usernames) >= 5:
                        break
            if len(available_usernames) >= 5:
                break

    # Step 4: Send results
    if available_usernames:
        await update.message.reply_text(
            "Available usernames:\n" + "\n".join([f"@{username}" for username in available_usernames])
        )
    else:
        await update.message.reply_text("Could not find any available usernames. Please try again.")

# Command: Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Username Generator Bot! 🎉\n\n"
        "Commands:\n"
        "/generate - Generate meaningful and available Telegram usernames.\n"
        "/help - Get instructions on using this bot."
    )

# Command: Help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "How to Use the Username Generator Bot:\n\n"
        "1. Use /generate to generate usernames using random meaningful words.\n"
        "2. The bot will check for username availability on Telegram and return 5 available options.\n\n"
        "Enjoy creating unique and meaningful usernames!"
    )

# Main function to run the bot
def main():
    # Build the application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("generate", generate_usernames))

    # Run the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
