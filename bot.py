from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random
import aiohttp
import asyncio

# Telegram bot token
BOT_TOKEN = "7388530009:AAF2P_-bFssTjnIKT1O-MjFLS2q4QPFnJTY"

# Owner ID
OWNER_ID = 7640331919

# In-memory storage for approved users
approved_users = set()

# Vast list of Hindi words
HINDI_WORDS = [
    # Emotions and Traits
    "Prem", "Daya", "Shaanti", "Anand", "Veerta", "Satya", "Gyaan", "Bhakti", "Vishwas", "Sammaan",
    # Nature and Elements
    "Chand", "Suraj", "Vayu", "Jal", "Prithvi", "Aakash", "Agni", "Hawa", "Barish", "Ganga",
    # Mythology
    "Ram", "Krishna", "Hanuman", "Sita", "Durga", "Lakshmi", "Ganesh", "Vishnu", "Shiva", "Parvati", 
    "Kali", "Saraswati", "Indra", "Karan", "Arjun", "Bheem", "Ravan",
    # Professions and Roles
    "Guru", "Raja", "Rani", "Yodha", "Sipahi", "Kavi", "Kalakar", "Vidyarthi", "Netaji",
    # Miscellaneous
    "Swarg", "Mukti", "Jeevan", "Adarsh", "Aatma", "Bhavishya", "Samarpan", "Vijay"
]

# Helper: Check username availability using Telegram's API
async def check_username(username: str) -> bool:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat"
    payload = {"chat_id": f"@{username}"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            data = await response.json()
            return not data.get("ok", False) and "not found" in data.get("description", "").lower()

# Command: Approve a user by user ID
async def approve_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    if not context.args or len(context.args) != 1:
        await update.message.reply_text("Usage: /approve <user_id>")
        return

    try:
        user_id = int(context.args[0])
        approved_users.add(user_id)
        await update.message.reply_text(f"User {user_id} has been approved.")
    except ValueError:
        await update.message.reply_text("Invalid user ID. Please provide a numeric user ID.")

# Command: Generate usernames with Hindi words
async def generate1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID and user_id not in approved_users:
        await update.message.reply_text("You are not approved to use this bot. Contact the bot owner for access.")
        return

    await update.message.reply_text("Generating 100 Hindi-based usernames and checking availability...")

    available_usernames = set()
    random_words = random.sample(HINDI_WORDS, len(HINDI_WORDS))  # Use all Hindi words for diversity

    async with aiohttp.ClientSession() as session:
        tasks = []
        for word in random_words:
            username = word.lower()
            tasks.append(check_username(username))
            if len(available_usernames) >= 100:
                break

        results = await asyncio.gather(*tasks)
        for word, available in zip(random_words, results):
            if available:
                available_usernames.add(f"@{word}")
                if len(available_usernames) >= 100:
                    break

    response = (
        "Generated meaningful and available Hindi usernames:\n" + "\n".join(available_usernames)
        if available_usernames
        else "Could not find any available usernames. Please try again."
    )
    await update.message.reply_text(response)

# Command: Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Username Generator Bot!\n\n"
        "Commands:\n"
        "/generate1 - Generate 100 Hindi-based usernames automatically.\n"
        "/approve - Approve a user by user ID (Owner only).\n"
        "/help - Get instructions."
    )

# Command: Help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Use /generate1 to automatically create 100 Hindi-based usernames. "
        "Only approved users can use this bot. Contact the owner for access."
    )

# Main function to run the bot
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("approve", approve_user))
    application.add_handler(CommandHandler("generate1", generate1))
    application.run_polling()

if __name__ == "__main__":
    main()
