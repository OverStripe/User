import random
import aiohttp
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)

# ✅ Bot Configuration
BOT_TOKEN = "7371066438:AAHQPNv8X0CzZaWI1CqPdeFhkg7QUUY1Qso"
OWNER_ID = 7640331919  # Replace with your Telegram user ID

# ✅ In-Memory Storage
approved_users = set()
checked_usernames = set()

# ✅ Enhanced Word List for Usernames
WORD_LIST = [
    # 🌌 Mystical & Fantasy
    "arcane", "ethereal", "phantom", "mythic", "seraphic", "celestial", "spectral", "aether", "void",
    "eclipse", "nebula", "zephyr", "luminous", "radiant", "aurora", "obsidian", "shadow", "onyx", "spirit",
    "crimson", "ember", "rift", "zenith", "glimmer", "oracle", "whisper",

    # 🚀 Tech & Sci-Fi
    "cypher", "nova", "quartz", "synthetic", "binary", "hologram", "quantum", "flux", "nexus", "fusion",
    "spark", "glitch", "ether", "horizon", "matrix", "circuit", "byte", "pulse", "logic", "signal", "data",

    # 🌿 Nature & Elements
    "ocean", "forest", "blossom", "raven", "willow", "dawn", "dusk", "flame", "ice", "frost", "storm",
    "rain", "breeze", "river", "thunder", "lotus", "fern", "ash", "gale", "serenity", "cascade", "glacier",

    # 💎 Elegant & Stylish
    "prime", "elite", "luxe", "royal", "noble", "vivid", "clarity", "zen", "sublime", "halo", "aura",
    "stride", "catalyst", "odyssey", "haven", "arcadia", "elegance", "lucid", "gleam", "solace", "velvet",

    # 🎮 Gaming & Modern
    "sniper", "blaze", "fury", "omen", "phantasm", "vortex", "arc", "drift", "smoke", "flare", "venom",
    "razor", "stealth", "strike", "rogue", "blade", "prowler", "zero", "nightshade", "firefly", "reboot"
]

# ============================
# ✅ Helper Function: Check Username
# ============================

async def check_username(username: str) -> bool:
    """Check if a username is available on Telegram."""
    if username in checked_usernames:
        return False

    checked_usernames.add(username)
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat"
    payload = {"chat_id": f"@{username}"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(telegram_url, json=payload) as response:
                data = await response.json()
                return not data.get("ok", False) and "not found" in data.get("description", "").lower()
    except Exception as e:
        print(f"Error checking username {username}: {e}")
        return False

# ============================
# ✅ Commands
# ============================

# ✅ /start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome Message"""
    await update.message.reply_text(
        "👋 **Welcome to the Enhanced Username Finder Bot!**\n\n"
        "Commands:\n"
        "• `/generate` - Generate a random available username.\n"
        "• `/generate @username` - Check if a specific username is available.\n"
        "• `/generate_bulk` - Generate and check 1,000 usernames.\n"
        "• `/approve <user_id>` - Approve a user (Owner only).\n"
        "• `/help` - Get help instructions.\n\n"
        "Enjoy finding the perfect username!"
    )

# ✅ /help Command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help Command"""
    await update.message.reply_text(
        "🛠 **How to Use:**\n"
        "1️⃣ `/generate` - Generate a random available username.\n"
        "2️⃣ `/generate @username` - Check if a specific username is available.\n"
        "3️⃣ `/generate_bulk` - Generate and check 1,000 usernames.\n"
        "4️⃣ Click '🔄 Generate Another Username' to search again.\n\n"
        "⚠️ Only approved users can generate usernames. Contact the owner for access."
    )

# ✅ /approve Command
async def approve_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Approve a user"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return

    if not context.args or len(context.args) != 1:
        await update.message.reply_text("Usage: /approve <user_id>")
        return

    try:
        user_id = int(context.args[0])
        approved_users.add(user_id)
        await update.message.reply_text(f"✅ User {user_id} has been approved.")
    except ValueError:
        await update.message.reply_text("⚠️ Invalid user ID. Please provide a numeric user ID.")

# ✅ /generate Command
async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate or check a specific username's availability."""
    user_id = update.effective_user.id
    if user_id != OWNER_ID and user_id not in approved_users:
        await update.message.reply_text("❌ You are not approved to use this bot.")
        return

    if context.args:
        username = context.args[0].strip("@").lower()
        if await check_username(username):
            await update.message.reply_text(f"✅ Username @{username} is available!")
        else:
            await update.message.reply_text(f"❌ Username @{username} is taken.")
    else:
        for _ in range(5):
            username = random.choice(WORD_LIST).lower()
            if await check_username(username):
                await update.message.reply_text(f"✅ Found available username: @{username}")
                return
        await update.message.reply_text("❌ No available usernames found in 5 attempts.")

# ✅ /generate_bulk Command
async def generate_bulk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate 1,000 usernames and check availability."""
    available_usernames = []
    for _ in range(1000):
        username = random.choice(WORD_LIST).lower()
        if await check_username(username):
            available_usernames.append(username)
    await update.message.reply_text(f"✅ Available Usernames:\n" + "\n".join(available_usernames))

# ✅ Main Function
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("approve", approve_user))
    application.add_handler(CommandHandler("generate", generate))
    application.add_handler(CommandHandler("generate_bulk", generate_bulk))
    application.run_polling()

# Run Bot
if __name__ == "__main__":
    main()
