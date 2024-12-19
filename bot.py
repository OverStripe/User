from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random
import aiohttp
import nltk
from nltk.corpus import words
from datetime import datetime, timedelta
import asyncio

# Telegram bot token
BOT_TOKEN = "7787236358:AAEiDQNthIY6GWZyfkc8qbW-Cw-uDJUwtOo"

# Owner ID
OWNER_ID = 7640331919

# In-memory storage for approvals
approved_users = {}

# Ensure the NLTK word list is downloaded
nltk.download("words")
WORD_LIST = words.words()

# Generate short meaningful words (5-12 characters)
SHORT_WORD_LIST = [word for word in WORD_LIST if 5 <= len(word) <= 12 and word.isalpha()]

# Prefixes and suffixes for username generation
PREFIXES = [
    "Eco", "Bright", "Dream", "Green", "Happy", "Blue", "Smart", "Alpha", "Beta", "Neo",
    "Aero", "Quantum", "Hyper", "Astro", "Golden", "Silver", "Next", "Power", "Mega",
    "Ultra", "Vision", "Prime", "Future", "Dynamic", "Magic", "Fast", "Strong", "Clear",
    "Pure", "Active", "Royal", "Epic", "True", "Vital", "Max", "Star", "Nova", "Core"
]

SUFFIXES = [
    "Land", "Zone", "Nest", "Haven", "Path", "Mind", "Way", "Stream", "Flow", "Base",
    "Edge", "Point", "Sky", "World", "Verse", "Vibes", "Place", "Life", "Hub", "Cloud",
    "Force", "Track", "Trail", "Port", "Peak", "Bridge", "Realm", "Shore", "Field",
    "Light", "Spark", "Rise", "Pulse", "Scope", "Focus", "Shift", "Glow", "Sphere", "Link"
]

# Helper: Parse duration strings (e.g., "1D", "1H")
def parse_duration(duration_str: str) -> timedelta:
    try:
        if duration_str.endswith("D"):
            return timedelta(days=int(duration_str[:-1]))
        elif duration_str.endswith("H"):
            return timedelta(hours=int(duration_str[:-1]))
    except ValueError:
        pass
    return None

# Helper: Check if a user is approved
def is_user_approved(user_id: int) -> bool:
    if user_id == OWNER_ID:
        return True  # Owner is always approved
    if user_id in approved_users:
        if approved_users[user_id] > datetime.now():
            return True
        else:
            del approved_users[user_id]  # Remove expired approval
    return False

# Middleware: Ensure only approved users can use commands
async def ensure_approved(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_user_approved(user_id):
        return True
    # Notify user to contact the owner for approval
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text="You are not approved to use this bot. Please contact @YourTelegramUsername to request access."
        )
    except Exception as e:
        print(f"Error sending DM to {user_id}: {e}")
    return False

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

# Command: Approve users
async def approve_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Usage: /approve <user_id> <duration (e.g., 1D, 1H)>")
        return

    try:
        user_id = int(context.args[0])
        duration = parse_duration(context.args[1])
        if not duration:
            await update.message.reply_text("Invalid duration format. Use 1D (days) or 1H (hours).")
            return

        # Approve user
        approved_users[user_id] = datetime.now() + duration
        expiration = approved_users[user_id].strftime("%Y-%m-%d %H:%M:%S")
        await update.message.reply_text(f"User {user_id} approved until {expiration}.")
    except ValueError:
        await update.message.reply_text("Invalid user ID. Please provide a numeric user ID.")

# Command: Make usernames
async def make_usernames(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await ensure_approved(update, context):
        return

    word_count = 5  # Default word count
    if context.args:
        try:
            word_count = int(context.args[0])
            if word_count not in [5, 6, 7, 8]:
                raise ValueError
        except ValueError:
            await update.message.reply_text("Please provide a valid word count (5, 6, 7, or 8).")
            return

    await update.message.reply_text(f"Generating {word_count}-word meaningful and available usernames...")

    available_usernames = set()
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(50):  # Try up to 50 combinations
            words = random.sample(SHORT_WORD_LIST, word_count)
            username = "".join(words).lower()
            if len(username) <= 32:
                tasks.append(check_username(username))

        results = await asyncio.gather(*tasks)
        for i, result in enumerate(results):
            if result:
                available_usernames.add(f"@{username}")

    response = (
        "Generated meaningful and available usernames:\n" + "\n".join(available_usernames)
        if available_usernames
        else "Could not find any available usernames. Please try again."
    )
    await update.message.reply_text(response)

# Command: Generate 20-30 usernames
async def generate_usernames(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await ensure_approved(update, context):
        return

    await update.message.reply_text("Generating 20-30 meaningful usernames and checking availability...")

    available_usernames = set()
    random_words = random.sample(SHORT_WORD_LIST, 20)

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
        "/make <word_count> - Generate 5, 6, 7, or 8-word meaningful usernames.\n"
        "/generate - Generate 20-30 meaningful usernames automatically.\n"
        "/approve - Owner-only command to approve users.\n"
        "/help - Get instructions."
    )

# Command: Help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Use /make to generate meaningful usernames with a specified word count (5-8). "
        "Use /generate to automatically create 20-30 meaningful usernames and check availability."
    )

# Main function to run the bot
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("approve", approve_user))
    application.add_handler(CommandHandler("make", make_usernames))
    application.add_handler(CommandHandler("generate", generate_usernames))
    application.run_polling()

if __name__ == "__main__":
    main()
