import asyncio
import logging

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from app.config import settings
from app.bot.commands import cmd_start, cmd_queue, cmd_style, cmd_plan, post_init
from app.bot.handlers import handle_idea, handle_generate_post, handle_list_ideas, handle_status
from app.db.init import init_db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    asyncio.run(init_db())

    app = (
        ApplicationBuilder()
        .token(settings.telegram_bot_token)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_start))
    app.add_handler(CommandHandler("post", handle_generate_post))
    app.add_handler(CommandHandler("list", handle_list_ideas))
    app.add_handler(CommandHandler("queue", cmd_queue))
    app.add_handler(CommandHandler("status", handle_status))
    app.add_handler(CommandHandler("style", cmd_style))
    app.add_handler(CommandHandler("plan", cmd_plan))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_idea))

    logger.info("Bot gestartet. Warte auf Nachrichten...")
    app.run_polling()


if __name__ == "__main__":
    main()
