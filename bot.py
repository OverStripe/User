from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random
import aiohttp
import asyncio

# Telegram bot token
BOT_TOKEN = "7388530009:AAHcVTFhxujN8ZJ2-sOwVq5dmR6aMlLtI1A"

# Owner ID
OWNER_ID = 7640331919

# In-memory storage for approved users
approved_users = set()

# Vast word list for stylish, trendy usernames
WORD_LIST = [
    "revamped", "reborn", "arcane", "stellar", "eclipse", "phantom", "shadow", "mythic", "ethereal",
    "luminous", "celestial", "spectral", "crimson", "vortex", "radiant", "zephyr", "infinite", "nova",
    "valiant", "glacial", "seraphic", "aether", "nebula", "void", "elegant", "primal", "lucid", "sublime",
    "aqua", "onyx", "ember", "halo", "blaze", "dusk", "dawn", "flare", "frost", "mist", "rift", "pulse",
    "zenith", "aspire", "flux", "spirit", "zen", "wisp", "glyph", "echo", "orbit", "quartz", "ignite",
    "solace", "rift", "haven", "arcadia", "soar", "catalyst", "fusion", "arc", "haven", "nova", "flare",
    "shade", "spark", "vivid", "stride", "bound", "clarity", "titan", "bliss", "novae", "prime", "aura",
    "cypher", "horizon", "pulse", "stellar", "epoch", "zen", "vibe", "spire", "odyssey", "luxe"
]

# Helper: Check username availability using Telegram's API
async def check_username(username: str) -> bool:
    """Checks if a username is available on Telegram."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat"
    payload = {"chat_id": f"@{username}"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            data = await response.json()
            return not data.get("ok", False) and "not found" in data.get("description", "").lower()

# Command: Approve a user by user ID
async def approve_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Approve a user to use the bot (Owner only)."""
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

# Command: Generate a username
async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate usernames and keep trying until a valid one is found."""
    user_id = update.effective_user.id
    if user_id != OWNER_ID and user_id not in approved_users:
        await update.message.reply_text("You are not approved to use this bot. Contact the bot owner for access.")
        return

    await update.message.reply_text("Generating usernames. This may take a moment...")

    async with aiohttp.ClientSession() as session:
        while True:  # Keep trying until a valid username is found
            username = random.choice(WORD_LIST).lower()
            if len(username) < 5 or len(username) > 15:  # Ensure Telegram constraints
                continue

            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat"
            payload = {"chat_id": f"@{username}"}

            async with session.post(url, json=payload) as response:
                data = await response.json()
                if not data.get("ok", False) and "not found" in data.get("description", "").lower():
                    await update.message.reply_text(f"Found available username: @{username}")
                    return  # Exit loop once a valid username is found

# Command: Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message and list available commands."""
    await update.message.reply_text(
        "Welcome to the Username Finder Bot!\n\n"
        "Commands:\n"
        "/generate - Generate a single available username.\n"
        "/approve - Approve a user by user ID (Owner only).\n"
        "/help - Get instructions."
    )

# Command: Help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message explaining how to use the bot."""
    await update.message.reply_text(
        "Use /generate to create an available username. "
        "Only approved users can use this bot. Contact the owner for access."
    )

# Main function to run the bot
def main():
    """Run the bot."""
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("approve", approve_user))
    application.add_handler(CommandHandler("generate", generate))
    application.run_polling()

if __name__ == "__main__":
    main()
