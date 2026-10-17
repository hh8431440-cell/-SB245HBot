import logging
import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Logging setup
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables & Configuration
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

WELCOME_MESSAGE = (
    "⚽ **GoalZone Sports Bot** brings you daily football updates, "
    "match fixtures, trivia, and live game insights instantly."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command for users with a clean, policy-compliant menu."""
    user = update.effective_user
    if not update.message:
        return

    keyboard = [
        [
            InlineKeyboardButton("🗓️ Today's Fixtures", callback_data="fixtures"),
            InlineKeyboardButton("🏆 Top Leagues", callback_data="leagues")
        ],
        [
            InlineKeyboardButton("🧠 Sports Trivia", callback_data="trivia"),
            InlineKeyboardButton("ℹ️ About Bot", callback_data="about")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    full_text = (
        f"Hello {user.first_name}! 👋\n\n"
        f"{WELCOME_MESSAGE}\n\n"
        "Choose an option below or type any question about football to chat!"
    )
    await update.message.reply_text(text=full_text, reply_markup=reply_markup, parse_mode="Markdown")


async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles button selections safely."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "fixtures":
        text = (
            "🗓️ **Today's Featured Match Fixtures:**\n\n"
            "• **Premier League:** Arsenal vs Chelsea - 20:00 UTC\n"
            "• **La Liga:** Real Madrid vs Barcelona - 21:00 UTC\n"
            "• **Champions League:** Bayern vs PSG - 19:00 UTC"
        )
        await query.message.reply_text(text, parse_mode="Markdown")

    elif data == "leagues":
        text = (
            "🏆 **Supported Leagues & Competitions:**\n\n"
            "1. English Premier League (EPL)\n"
            "2. UEFA Champions League (UCL)\n"
            "3. Spanish La Liga\n"
            "4. Italian Serie A"
        )
        await query.message.reply_text(text, parse_mode="Markdown")

    elif data == "trivia":
        text = (
            "🧠 **Football Trivia Question:**\n\n"
            "Which player has won the most Ballon d'Or awards?\n"
            "_Hint: He has won 8 titles!_\n\n"
            "Reply with your answer to chat!"
        )
        await query.message.reply_text(text, parse_mode="Markdown")

    elif data == "about":
        text = (
            "ℹ️ **About GoalZone Bot:**\n\n"
            "This bot provides clean sports updates, schedules, and fan discussions. "
            "Fully compliant with platform guidelines."
        )
        await query.message.reply_text(text, parse_mode="Markdown")


async def handle_sports_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responds to user sports queries using keyless AI text generation."""
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    status_msg = await update.message.reply_text("Thinking... ⚽")

    try:
        response = requests.post(
            "https://text.pollinations.ai/",
            json={
                "messages": [
                    {"role": "system", "content": "You are a friendly, knowledgeable sports and football expert."},
                    {"role": "user", "content": user_text}
                ]
            },
            timeout=25
        )
        if response.status_code == 200:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id,
                text=response.text
            )
        else:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id,
                text="⚠️ Sports assistant is busy right now. Try again shortly."
            )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=status_msg.message_id,
            text="⚠️ Could not process your request."
        )


def main() -> None:
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is missing!")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_sports_chat))

    logger.info("GoalZone Sports Bot worker starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
