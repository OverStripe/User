from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random
import aiohttp
import asyncio

# Telegram bot token
BOT_TOKEN = "7388530009:AAEzpe7mSSd5mKYVq6hFkoR7yMX-2vuaU_0"

# Owner ID
OWNER_ID = 7640331919

# In-memory storage for approved users
approved_users = set()

# Words, prefixes, suffixes, and anime names for username generation
PREFIXES = ["Super", "Mega", "Ultra", "Hyper", "Elite", "Cool", "Swift", "Star", "Power", "Shadow", "Neo", "Alpha"]
SUFFIXES = ["Master", "Pro", "Hero", "King", "Queen", "Ace", "Boss", "Ninja", "Sensei", "Samurai"]
ADJECTIVES = ["Happy", "Brave", "Smart", "Bold", "Clever", "Mighty", "Bright", "Fierce", "Epic", "Glorious"]
NOUNS = ["Tiger", "Eagle", "Phoenix", "Lion", "Falcon", "Wolf", "Shark", "Panther", "Dragon", "Blade"]

# Anime-related terms and names
ANIME_NAMES = [
    "Naruto", "Sasuke", "Sakura", "Kakashi", "Itachi", "Goku", "Vegeta", "Luffy", "Zoro", "Nami", 
    "Mikasa", "Eren", "Levi", "Armin", "Killua", "Gon", "Hisoka", "Astro", "Inuyasha", "Haku", 
    "Jiraiya", "Rengoku", "Tanjirou", "Nezuko", "Zenitsu", "Gojo", "Satoru", "Yuji", "Kaguya", "Shiro", 
    "ZeroTwo", "Kaneki", "Ichigo", "Rukia", "Aizen", "Shoto", "Deku", "Bakugo", "Erza", "Natsu", 
    "Gray", "Lucy", "Meliodas", "Elizabeth", "Ban", "Escanor", "Shinobu", "Sanemi", "Tomioka", "Rukia"
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

# Command: Generate usernames
async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID and user_id not in approved_users:
        await update.message.reply_text("You are not approved to use this bot. Contact the bot owner for access.")
        return

    # Set max length (default: 20 characters)
    max_length = 20
    if context.args:
        try:
            max_length = int(context.args[0])
            if max_length < 5 or max_length > 30:
                raise ValueError
        except ValueError:
            await update.message.reply_text("Invalid length. Please provide a number between 5 and 30.")
            return

    await update.message.reply_text(f"Generating usernames with a maximum length of {max_length} characters...")

    available_usernames = set()
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(300):  # Generate a larger pool for better results
            # Combine components dynamically
            username = random.choice(PREFIXES) + random.choice(ADJECTIVES) + random.choice(NOUNS + ANIME_NAMES)
            if len(username) > max_length:
                continue
            username = username[:max_length].lower()  # Ensure length constraint
            tasks.append(check_username(username))
            if len(available_usernames) >= 100:
                break

        results = await asyncio.gather(*tasks)
        for task, available in zip(tasks, results):
            if available:
                available_usernames.add(f"@{task}")
                if len(available_usernames) >= 100:
                    break

    response = (
        "Generated meaningful and available usernames:\n" + "\n".join(available_usernames)
        if available_usernames
        else "Could not find any available usernames. Please try again."
    )
    await update.message.reply_text(response)

# Command: Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Anime Username Generator Bot!\n\n"
        "Commands:\n"
        "/generate <max_length> - Generate 100 cool usernames (default max length: 20).\n"
        "/approve - Approve a user by user ID (Owner only).\n"
        "/help - Get instructions."
    )

# Command: Help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Use /generate <max_length> to create 100 cool usernames. "
        "You can specify a maximum length for the usernames (default: 20). "
        "Only approved users can use this bot. Contact the owner for access."
    )

# Main function to run the bot
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("approve", approve_user))
    application.add_handler(CommandHandler("generate", generate))
    application.run_polling()

if __name__ == "__main__":
    main()
