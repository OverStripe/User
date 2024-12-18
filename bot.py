import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import aiohttp
import nltk
from nltk.corpus import words

BOT_TOKEN = "7371066438:AAHXTmNKuLQOF1ZA2q-uv7JLxwPtd_6YKNE"

# Download NLTK data
nltk.download("words")

# Load a filtered word list (short meaningful words only)
ALL_WORDS = words.words()
SHORT_MEANINGFUL_WORDS = [
    word for word in ALL_WORDS if 5 <= len(word) <= 12 and word.isalpha()
]

# Check if a username is available
async def check_username(username):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat"
    payload = {"chat_id": f"@{username}"}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            data = await response.json()
            return not data.get("ok", False)  # True if username is available

# Generate short meaningful usernames
def generate_single_word_usernames(count=10):
    return random.sample(SHORT_MEANINGFUL_WORDS, count)

# Add slight variations to usernames
def generate_variations(word):
    return [
        f"{word}ly",
        f"{word}s",
        f"{word}ing",
        f"the{word}",
        f"my{word}",
        f"{word}er",
    ]

# Command to generate usernames
async def generate_available(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Generating usernames similar to: titters, retrying, oddest, scrawl...")

    # Step 1: Generate single words
    single_words = generate_single_word_usernames()
    await update.message.reply_text(f"Generated words: {', '.join(single_words)}")

    available_usernames = []
    attempts = 0

    # Step 2: Check availability of single words
    for word in single_words:
        if await check_username(word):
            available_usernames.append(word)
            if len(available_usernames) >= 5:
                break

    # Step 3: If fewer than 5 usernames, try variations
    if len(available_usernames) < 5:
        await update.message.reply_text("Single-word usernames not sufficient. Trying variations...")
        for word in single_words:
            variations = generate_variations(word)
            for variation in variations:
                if await check_username(variation):
                    available_usernames.append(variation)
                    if len(available_usernames) >= 5:
                        break
            if len(available_usernames) >= 5:
                break

    # Step 4: Respond with available usernames
    if available_usernames:
        await update.message.reply_text(
            "Available usernames:\n" + "\n".join([f"@{u}" for u in available_usernames])
        )
    else:
        await update.message.reply_text("Could not find any available usernames. Please try again.")

# Command to start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Username Generator Bot! 🎉\n\n"
        "Commands:\n"
        "/generatewords - Generate usernames similar to titters, retrying, oddest, scrawl.\n"
        "/help - Get detailed instructions on how to use this bot."
    )

# Command to show help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "How to Use the Username Generator Bot:\n\n"
        "1. Use /generatewords to generate usernames using short, meaningful words.\n"
        "   The bot will first check single-word usernames, then create slight variations.\n\n"
        "Enjoy creating unique and meaningful usernames!"
    )

# Main function to set up the bot
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("generatewords", generate_available))

    # Start the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
