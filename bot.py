from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random
import aiohttp
import nltk
from nltk.corpus import words
from datetime import datetime, timedelta
import asyncio

# Telegram bot token
BOT_TOKEN = "7388530009:AAHOgu6S-ISp5W-H5-V1JMhxH1wgoZB2DEk"

# Owner ID
OWNER_ID = 7640331919

# In-memory storage for approvals
approved_users = {}

# Ensure the NLTK word list is downloaded
nltk.download("words")
WORD_LIST = words.words()

# Generate short meaningful words (5-12 characters)
SHORT_WORD_LIST = [word for word in WORD_LIST if 5 <= len(word) <= 12 and word.isalpha()]

# Expanded Prefixes and Suffixes
PREFIXES = [
    "Eco", "Bright", "Dream", "Green", "Happy", "Blue", "Smart", "Alpha", "Beta", "Neo",
    "Aero", "Quantum", "Hyper", "Astro", "Golden", "Silver", "Next", "Power", "Mega",
    "Ultra", "Vision", "Prime", "Future", "Dynamic", "Magic", "Fast", "Strong", "Clear",
    "Pure", "Active", "Royal", "Epic", "True", "Vital", "Max", "Star", "Nova", "Core",
    "Luna", "Cosmo", "Pixel", "Cloud", "Turbo", "Bold", "Cyber", "Tech", "Bright", "Zeta",
    "Vivid", "Solar", "Spark", "Infinity", "Stellar", "Ocean", "Harmony", "Brave", "Hero"
]

SUFFIXES = [
    "Land", "Zone", "Nest", "Haven", "Path", "Mind", "Way", "Stream", "Flow", "Base",
    "Edge", "Point", "Sky", "World", "Verse", "Vibes", "Place", "Life", "Hub", "Cloud",
    "Force", "Track", "Trail", "Port", "Peak", "Bridge", "Realm", "Shore", "Field",
    "Light", "Spark", "Rise", "Pulse", "Scope", "Focus", "Shift", "Glow", "Sphere", "Link",
    "Craft", "Center", "Axis", "Front", "Horizon", "Vault", "Union", "Circuit", "System", "Mode"
]

# Helper: Check username availability using Telegram's API
async def check_username(username: str) -> bool:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat"
    payload = {"chat_id": f"@{username}"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            data = await response.json()
            return not data.get("ok", False) and "not found" in data.get("description", "").lower()

# Helper: Generate meaningful variations with prefixes and suffixes
async def check_and_add_variations(word, available_usernames, session):
    variations = [f"{prefix}{word}" for prefix in PREFIXES] + [f"{word}{suffix}" for suffix in SUFFIXES]
    random.shuffle(variations)  # Shuffle for variety

    for variation in variations[:10]:  # Limit to 10 variations per word
        username = variation.lower()
        if await check_username(username):
            available_usernames.add(f"@{variation}")

# Command: Generate 100 usernames
async def generate_usernames(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID and user_id not in approved_users:
        await update.message.reply_text("You are not approved to use this bot. Contact the bot owner for access.")
        return

    await update.message.reply_text("Generating 100 meaningful usernames and checking availability...")

    available_usernames = set()
    random_words = random.sample(SHORT_WORD_LIST, 50)  # Use 50 base words for diversity

    async with aiohttp.ClientSession() as session:
        tasks = [check_and_add_variations(word, available_usernames, session) for word in random_words]
        await asyncio.gather(*tasks)

    response = (
        "Generated meaningful and available usernames:\n" + "\n".join(available_usernames)
        if available_usernames
        else "Could not find any available usernames. Please try again."
    )
    await update.message.reply_text(response)

# Command: Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Username Generator Bot!\n\n"
        "Commands:\n"
        "/generate - Generate 100 meaningful usernames automatically.\n"
        "/help - Get instructions."
    )

# Command: Help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Use /generate to automatically create 100 meaningful usernames and check availability."
    )

# Main function to run the bot
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("generate", generate_usernames))
    application.run_polling()

if __name__ == "__main__":
    main()
