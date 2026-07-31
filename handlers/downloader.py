import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from services.youtube import download_ytv_and_zip
from database.db import set_data, get_data
import config


async def select_format(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a format selection menu."""
    url = update.message.text

    set_data(update.effective_chat.id, {
        "url": url,
        "status": "started",
    })

    keyboard = [
        [
            InlineKeyboardButton("Audio", callback_data="mp3"),
            InlineKeyboardButton("Video", callback_data="mp4"),
        ],
        [InlineKeyboardButton("Cancel", callback_data="cancel")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Great\\! How would you like to download your video?\n\n"
        "🎵 *Audio \\(MP3\\)* – Best for music and podcasts\\.\n"
        "📹 *Video \\(MP4\\)* – Watch in full quality\\.\n\n"
        "Tap a button below to choose:",
        reply_markup=reply_markup,
        parse_mode="MarkdownV2",
    )


async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles user selection for audio/video format."""
    query = update.callback_query
    selected_format = query.data

    await query.answer()
    chat_id = update.effective_chat.id
    user_data = get_data(chat_id)

    if selected_format == "mp3":
        await query.edit_message_text(
            "🎶 *You chose Audio \\(MP3\\)\\!* Preparing your download\\.\\.\\.",
            parse_mode="MarkdownV2",
        )
    elif selected_format == "mp4":
        await query.edit_message_text(
            "📺 *You chose Video \\(MP4\\)\\!* Fetching your file\\.\\.\\.",
            parse_mode="MarkdownV2",
        )
    else:
        await query.edit_message_text(
            "❌ *Download canceled\\.* Let me know if you need anything else\\!",
            parse_mode="MarkdownV2",
        )
        return

    if not user_data or not user_data.get("url"):
        await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ I lost track of your link — please send the YouTube URL again.",
        )
        return

    zip_file_path = None
    try:
        zip_file_path = await download_ytv_and_zip(user_data["url"], selected_format)

        file_size = os.path.getsize(zip_file_path)
        if file_size > config.MAX_UPLOAD_SIZE_BYTES:
            await context.bot.send_message(
                chat_id=chat_id,
                text=(
                    f"⚠️ The result is {file_size / (1024 * 1024):.1f}MB, which is over "
                    f"Telegram's {config.MAX_UPLOAD_SIZE_MB}MB bot upload limit. "
                    "Try a shorter video or a smaller playlist."
                ),
            )
            return

        with open(zip_file_path, "rb") as f:
            await context.bot.send_document(
                chat_id=chat_id,
                document=f,
                filename=os.path.basename(zip_file_path),
                caption="Here is your zip file!",
                read_timeout=60,
                write_timeout=60,
            )
    except Exception as e:
        print(f"Error happened: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ Something went wrong while downloading that. Please check the link and try again.",
        )
    finally:
        if zip_file_path and os.path.exists(zip_file_path):
            os.remove(zip_file_path)
