from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random
import aiohttp
import nltk
from nltk.corpus import words
from datetime import datetime, timedelta

# Your Telegram bot token
BOT_TOKEN = "7787236358:AAHERPbXt8dGsxg8GcP9VVOmFPCrkn16X6Y"

# Owner ID
OWNER_ID = 7640331919

# In-memory storage for approvals
approved_users = {}

# Ensure the NLTK word list is downloaded
nltk.download("words")
WORD_LIST = words.words()

# Generate short meaningful words (5-12 characters)
SHORT_WORD_LIST = [word for word in WORD_LIST if 5 <= len(word) <= 12 and word.isalpha()]

# Generate meaningful and unique variations
def generate_meaningful_variations(base_word: str) -> list:
    prefixes = ["Eco", "Bright", "Dream", "Green", "Happy", "Blue", "Smart"]
    suffixes = ["Land", "Zone", "Nest", "Haven", "Path", "Mind", "Way"]
    meaningful_variations = [
        f"{prefix}{base_word}" for prefix in prefixes
    ] + [
        f"{base_word}{suffix}" for suffix in suffixes
    ]
    meaningful_variations.append(base_word)  # Include the base word
    return list(set(meaningful_variations))  # Ensure uniqueness

# Check username availability using Telegram's API
async def check_username(username: str) -> bool:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat"
    payload = {"chat_id": f"@{username}"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            data = await response.json()
            return not data.get("ok", False) and "not found" in data.get("description", "").lower()

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
            text="You are not approved to use this bot. Please contact @UnderThief to request access."
        )
    except Exception as e:
        print(f"Error sending DM to {user_id}: {e}")
    return False

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

# Command: Generate meaningful and unique usernames
async def generate_usernames(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await ensure_approved(update, context):
        return

    count = 10
    if context.args:
        try:
            count = min(20, max(1, int(context.args[0])))
        except ValueError:
            await update.message.reply_text("Please provide a valid number of usernames to generate (1-20).")
            return

    await update.message.reply_text(f"Generating {count} meaningful usernames...")

    random_words = random.sample(SHORT_WORD_LIST, count)
    available_usernames = set()

    for word in random_words:
        for variation in generate_meaningful_variations(word):
            if await check_username(variation.lower()):
                available_usernames.add(f"@{variation}")
                if len(available_usernames) >= count:
                    break
        if len(available_usernames) >= count:
            break

    if available_usernames:
        response = "Meaningful and available usernames:\n" + "\n".join(available_usernames)
    else:
        response = "Could not find any available usernames. Please try again."
    await update.message.reply_text(response)

# Command: Check usernames in bulk
async def check_usernames(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await ensure_approved(update, context):
        return

    if not context.args:
        await update.message.reply_text("Please provide usernames to check.")
        return

    usernames = [username.strip("@").strip() for username in " ".join(context.args).split()]
    results = []
    for username in usernames:
        if len(username) < 5 or len(username) > 32 or not username.isalnum():
            results.append(f"@{username} - Invalid username.")
            continue

        if await check_username(username):
            results.append(f"@{username} - Available ✅")
        else:
            results.append(f"@{username} - Unavailable ❌")

    await update.message.reply_text("\n".join(results))

# Command: Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Meaningful Username Generator Bot!\n\n"
        "Commands:\n"
        "/generate - Generate meaningful and unique Telegram usernames.\n"
        "/check - Check the availability of usernames.\n"
        "/approve - Owner-only command to approve users.\n"
        "/help - Get instructions."
    )

# Command: Help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Use /generate to generate meaningful usernames or /check to check availability. "
        "Only approved users can use this bot. Contact @UnderThief to request approval."
    )

# Main function to run the bot
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("approve", approve_user))
    application.add_handler(CommandHandler("generate", generate_usernames))
    application.add_handler(CommandHandler("check", check_usernames))
    application.run_polling()

if __name__ == "__main__":
    main()
