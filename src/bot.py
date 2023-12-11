"""Telegram bot for managing spendings."""
import logging
from collections import defaultdict
from typing import List

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.formatting import Bold, as_key_value, as_list, as_marked_section
from src.finances import SheetSpending, Spending
from src.phrase import HELP_MESSAGE, WELCOME_MESSAGE
from src.settings import MAX_SPENDINGS_IN_BULK_REQUESTS, TELEGRAM_BOT_TOKEN
from src.spreadsheets import add_spending as add_spending_spreadsheet
from src.spreadsheets import get_spendings

logging.basicConfig(level=logging.INFO)

bot_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
bot_commands = [
    types.BotCommand(command="start", description="Start the bot"),
    types.BotCommand(command="help", description="Help"),
    types.BotCommand(command="report", description="Generate report"),
]

bot = Bot(TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot=bot)


def generate_report_message(spendings: List[SheetSpending]) -> str:
    """
    Generate a report message from a list of spendings.

    Args:
        spendings (List[SheetSpending]): List of spendings to be included in the report.

    Returns:
        str: Formatted report message.
    """
    spendings_by_category: defaultdict[str, float] = defaultdict(float)
    total_spendings: float = 0
    for spending in spendings:
        total_spendings += spending.usd or 0
        spendings_by_category[spending.category] += spending.usd or 0

    if not spendings:
        return "No spendings found"

    return as_list(
        as_marked_section(
            Bold("Total spendings by category"),
            *[
                as_key_value(category, cost)
                for category, cost in spendings_by_category.items()
            ],
        ),
        as_marked_section(
            Bold("Summary:"),
            as_key_value("Total spendings", total_spendings),
            as_key_value("Total spendings records", len(spendings)),
            as_key_value(
                "Total days found",
                len({spnd.datetime.day for spnd in spendings}),
            ),
        ),
        sep="\n\n",
    ).as_markdown()


@dp.message(Command("start"))
async def send_welcome(message: types.Message) -> None:
    """
    Send a welcome message to the user.

    Args:
        message (types.Message): The message object from Telegram.
    """
    await message.reply(WELCOME_MESSAGE, parse_mode="Markdown")


@dp.message(Command("help"))
async def send_help(message: types.Message) -> None:
    """
    Send a help message.

    Args:
        message (types.Message): The message object from Telegram.
    """
    await message.reply(HELP_MESSAGE, parse_mode="Markdown")


@dp.message(Command("report"))
async def generate_report(message: types.Message) -> None:
    """
    Generate and send a spending report.

    Args:
        message (types.Message): The message object from Telegram.
    """
    logging.info(f"Generating report for message: {message}")

    if not message.text:
        await message.reply("No data provided")
        return

    arguments = [el.strip() for el in message.text.split(" ")]

    # remove headers
    arguments = arguments[1:]

    if len(arguments) != 1:
        await message.reply(
            "Pass only one argument - date in format YYYY-MM or YYYY-MM-DD",
        )
        return

    date_args = arguments[0].split("-")

    try:
        spendings: List[SheetSpending] = get_spendings(
            year=int(date_args[0]),
            month=int(date_args[1]),
            day=int(date_args[2]) if len(date_args) == 3 else None,
        )
    except ValueError as err:
        await message.reply(str(err))
        return

    await message.reply(generate_report_message(spendings), parse_mode="MarkdownV2")


@dp.message()
async def add_spending(message: types.Message) -> None:
    """
    Add a spending record.

    Args:
        message (types.Message): The message object containing the spending data.
    """
    logging.info(f"Adding spendings for message: {message}")
    if not message.text:
        await message.reply("No data provided")
        return

    spending_records = message.text.split("|")
    try:
        spending_objects = [
            Spending.from_string(record.strip()) for record in spending_records
        ]
        if spending_objects and len(spending_objects) > MAX_SPENDINGS_IN_BULK_REQUESTS:
            await message.reply(
                f"Message too long: {len(spending_objects)}",  # noqa:WPS237
            )
    except ValueError as error:
        await message.reply(str(error))
        return
    for spending in spending_objects:
        add_spending_spreadsheet(spending)
    await message.reply(
        f"Spendings added, count: {len(spending_objects)}",  # noqa:WPS237
    )


async def run_bot() -> None:
    """Run the Telegram bot."""
    await bot.set_my_commands(bot_commands)
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio  # noqa: WPS433

    asyncio.run(run_bot())
