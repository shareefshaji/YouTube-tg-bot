import logging

from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from handlers.start import start
from handlers.help import help_command
from handlers.downloader import select_format, download
from handlers.error import error_handler

import config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

YOUTUBE_URL_PATTERN = r"^(https?:\/\/)?(www\.)?(youtube\.com\/(watch\?v=|embed\/|playlist\?list=)|youtu\.be\/)[\w\-]+"

if __name__ == '__main__':
    if not config.BOT_TOKEN:
        raise SystemExit("BOT_TOKEN is not set. Add it to your .env file or environment variables.")

    application = (
        ApplicationBuilder()
        .token(config.BOT_TOKEN)
        .read_timeout(30)
        .write_timeout(30)
        .build()
    )

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(MessageHandler(filters.Regex(YOUTUBE_URL_PATTERN), select_format))
    application.add_handler(CallbackQueryHandler(download))
    application.add_error_handler(error_handler)

    application.run_polling()
