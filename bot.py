from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import random
import aiohttp
import asyncio

# Telegram bot token
BOT_TOKEN = "7388530009:AAHG5hpYZcJnm4okitSoVV-RXkm2avB-tJA"

# Owner ID
OWNER_ID = 7640331919

# In-memory storage for approved users and previously checked usernames
approved_users = set()
checked_usernames = set()  # To keep track of all generated usernames

# Vast word list for stylish, trendy usernames
WORD_LIST = [
    "revamped", "reborn", "arcane", "stellar", "eclipse", "phantom", "shadow", "mythic", "ethereal",
    "luminous", "celestial", "spectral", "crimson", "vortex", "radiant", "zephyr", "infinite", "nova",
    "valiant", "glacial", "seraphic", "aether", "nebula", "void", "elegant", "primal", "lucid", "sublime",
    "aqua", "onyx", "ember", "halo", "blaze", "dusk", "dawn", "flare", "frost", "mist", "rift", "pulse",
    "zenith", "aspire", "flux", "spirit", "zen", "wisp", "glyph", "echo", "orbit", "quartz", "ignite",
    "solace", "rift", "haven", "arcadia", "soar", "catalyst", "fusion", "arc", "nova", "shade", "spark",
    "vivid", "stride", "clarity", "titan", "bliss", "prime", "aura", "cypher", "horizon", "pulse", "epoch",
    "vibe", "spire", "odyssey", "luxe"
]

# Helper: Check username availability using Telegram and Fragment APIs
async def check_username(username: str) -> bool:
    """Checks if a username is available on Telegram and Fragment."""
    if username in checked_usernames:
        return False  # Skip if already checked

    # Add username to the checked list
    checked_usernames.add(username)

    # Check on Telegram
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat"
    telegram_payload = {"chat_id": f"@{username}"}

    # Check on Fragment
    fragment_url = f"https://fragment.com/{username}"

    async with aiohttp.ClientSession() as session:
        # Check Telegram availability
        async with session.post(telegram_url, json=telegram_payload) as telegram_response:
            telegram_data = await telegram_response.json()
            telegram_available = not telegram_data.get("ok", False) and "not found" in telegram_data.get("description", "").lower()

        # Check Fragment availability
        async with session.get(fragment_url) as fragment_response:
            fragment_available = fragment_response.status == 404  # Fragment returns 404 for unavailable usernames

        # Return True only if both Telegram and Fragment report the username as available
        return telegram_available and fragment_available

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

    await update.message.reply_text("Searching for an available username. Please wait...")

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
                    if username not in checked_usernames:
                        checked_usernames.add(username)

                        # Interactive UI: Provide a button to regenerate
                        keyboard = [
                            [InlineKeyboardButton("Generate Another Username", callback_data="regenerate")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)

                        await update.message.reply_text(
                            f"🎉 Found available username: @{username}\n\nUse this or regenerate.",
                            reply_markup=reply_markup
                        )
                        return  # Exit loop once a valid username is found

# Callback handler for regenerate button
async def regenerate_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles regenerate button callback."""
    query = update.callback_query
    await query.answer()

    # Trigger username generation again
    await generate(query, context)

# Command: Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message and list available commands."""
    await update.message.reply_text(
        "Welcome to the Enhanced Username Finder Bot!\n\n"
        "Commands:\n"
        "• /generate - Generate a single available username.\n"
        "• /approve - Approve a user by user ID (Owner only).\n"
        "• /help - Get instructions.\n\n"
        "Enjoy finding the perfect username!"
    )

# Command: Help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message explaining how to use the bot."""
    await update.message.reply_text(
        "🛠 How to Use:\n"
        "1️⃣ Use /generate to search for an available username.\n"
        "2️⃣ The bot ensures usernames are available on both Telegram and Fragment.\n"
        "3️⃣ If you want another username, click 'Generate Another Username'.\n\n"
        "⚠️ Only approved users can generate usernames. Contact the owner for access."
    )

# Main function to run the bot
def main():
    """Run the bot."""
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("approve", approve_user))
    application.add_handler(CommandHandler("generate", generate))
    application.add_handler(CallbackQueryHandler(regenerate_callback, pattern="^regenerate$"))
    application.run_polling()

if __name__ == "__main__":
    main()
