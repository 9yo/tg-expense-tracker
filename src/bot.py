"""Telegram bot for managing spendings."""
import logging
from io import BytesIO
from typing import Any, Optional

from aiogram import Bot, Dispatcher, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import BufferedInputFile  # noqa:WPS458
from src.finances import Spending
from src.phrase import HELP_MESSAGE, WELCOME_MESSAGE
from src.report_service import ReportService
from src.settings import MAX_SPENDINGS_IN_BULK_REQUESTS, TELEGRAM_BOT_TOKEN
from src.spreadsheets import add_spending as add_spending_spreadsheet

logging.basicConfig(level=logging.INFO)

bot_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
bot_commands = [
    types.BotCommand(command="start", description="Start the bot"),
    types.BotCommand(command="help", description="Help"),
    types.BotCommand(command="report", description="Generate report"),
]

bot = Bot(TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot=bot)


@dp.message(Command("start"))
async def send_welcome(message: types.Message) -> None:
    """
    Send a welcome message to the user.

    Args:
        message (types.Message): The message object from Telegram.
    """
    await safe_replay(message, WELCOME_MESSAGE, parse_mode="Markdown")


@dp.message(Command("help"))
async def send_help(message: types.Message) -> None:
    """
    Send a help message.

    Args:
        message (types.Message): The message object from Telegram.
    """
    await safe_replay(message, HELP_MESSAGE, parse_mode="Markdown")


@dp.message(Command("report"))
async def generate_report(message: types.Message) -> None:
    """
    Generate and send a spending report.

    Args:
        message (types.Message): The message object from Telegram.
    """
    logging.info(f"Generating report for message: {message}")

    if not message.text:
        await safe_replay(message, "No data provided")
        return

    arguments = [el.strip() for el in message.text.split(" ")]

    # remove headers
    arguments = arguments[1:]

    if len(arguments) != 1:
        await safe_replay(
            message,
            "Pass only one argument - date in format YYYY-MM or YYYY-MM-DD",
        )
        return

    report, photo = ReportService.generate_report(*arguments[0].split("-"))

    await safe_replay(
        message,
        photo=photo,
        caption=report,
        parse_mode="MarkdownV2",
    )


@dp.message()
async def add_spending(message: types.Message) -> None:
    """
    Add a spending record.

    Args:
        message (types.Message): The message object containing the spending data.
    """
    logging.info(f"Adding spendings for message: {message}")
    if not message.text:
        await safe_replay(message, "No data provided")
        return

    spending_records = message.text.split("|")
    try:
        spending_objects = [
            Spending.from_string(record.strip()) for record in spending_records
        ]
    except ValueError as error:
        await safe_replay(message, str(error))
        return
    add_spending_spreadsheet(spending_objects)
    await safe_replay(
        message,
        f"Spendings added, count: {len(spending_objects)}",  # noqa:WPS237
    )


async def safe_replay(
    message: types.Message,
    *args: Any,
    photo: Optional[BytesIO] = None,
    **kwargs: Any,
) -> None:
    try:
        if photo:
            await message.reply_photo(
                BufferedInputFile(photo.read(), filename="report.png"),
                *args,
                **kwargs,
            )
        else:
            await message.reply(*args, **kwargs)
    except TelegramBadRequest as err:
        logging.info("Replay not achieved, reason: TelegramBadRequest", err)


async def run_bot() -> None:
    """Run the Telegram bot."""
    await bot.set_my_commands(bot_commands)
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio  # noqa: WPS433

    asyncio.run(run_bot())
