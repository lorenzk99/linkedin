import asyncio
import logging

from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.config import settings
from app.bot.commands import (
    cmd_start,
    cmd_queue,
    cmd_style,
    cmd_style_import,
    cmd_style_done,
    cmd_plan,
    cmd_cluster,
    post_init,
)
from app.bot.handlers import (
    handle_idea,
    handle_generate_post,
    handle_list_ideas,
    handle_status,
    handle_callback,
)
from app.db.init import init_db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def error_handler(update, context):
    logger.error("Update %s verursachte Fehler: %s", update, context.error)
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "Ein Fehler ist aufgetreten. Bitte versuche es erneut."
        )


async def on_startup(application):
    await init_db()
    await post_init(application)


def main():
    app = (
        ApplicationBuilder()
        .token(settings.telegram_bot_token)
        .post_init(on_startup)
        .build()
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_start))
    app.add_handler(CommandHandler("post", handle_generate_post))
    app.add_handler(CommandHandler("list", handle_list_ideas))
    app.add_handler(CommandHandler("queue", cmd_queue))
    app.add_handler(CommandHandler("status", handle_status))
    app.add_handler(CommandHandler("style", cmd_style))
    app.add_handler(CommandHandler("style_import", cmd_style_import))
    app.add_handler(CommandHandler("style_done", cmd_style_done))
    app.add_handler(CommandHandler("cluster", cmd_cluster))
    app.add_handler(CommandHandler("plan", cmd_plan))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_idea))
    app.add_error_handler(error_handler)

    logger.info("Bot gestartet. Warte auf Nachrichten...")
    app.run_polling()


if __name__ == "__main__":
    main()
