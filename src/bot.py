from collections import defaultdict
from typing import List

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.formatting import as_list, Bold, as_key_value, as_marked_section, Text

from src.finances import Spending, SheetSpending
from src.phrase import WELCOME_MESSAGE, HELP_MESSAGE
from src.settings import TELEGRAM_BOT_TOKEN
from src.spreadsheets import add_spending as add_spending_spreadsheet, get_spendings


BOT_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
BOT_COMMANDS = [
    types.BotCommand(command="start", description="Start the bot"),
    types.BotCommand(command="help", description="Help"),
    types.BotCommand(command="report", description="Generate report")
]

bot = Bot(TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot=bot)


def generate_report_message(spendings: List[SheetSpending]) -> str:
    uniq_days = set([s.datetime.day for s in spendings])
    spendings_by_category = defaultdict(int)
    total_spendings = 0
    for spending in spendings:
        total_spendings += spending.usd
        spendings_by_category[spending.category] += spending.usd

    if not spendings:
        return "No spendings found"

    content: Text = as_list(
        as_marked_section(
            Bold("Total spendings by category"),
            *[as_key_value(category, cost) for category, cost in spendings_by_category.items()]
        ),
        as_marked_section(
            Bold("Summary:"),
            as_key_value("Total spendings", total_spendings),
            as_key_value("Total spendings records", len(spendings)),
            as_key_value("Total days found", len(uniq_days)),
        ),
        sep="\n\n",
    )

    return content.as_markdown()


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply(WELCOME_MESSAGE, parse_mode='Markdown')


@dp.message(Command("help"))
async def send_help(message: types.Message):
    await message.reply(HELP_MESSAGE, parse_mode='Markdown')


@dp.message(Command("report"))
async def generate_report(message: types.Message):
    print(f"Generating report for message: {message}")

    arguments = [el.strip() for el in message.text.split(' ')]

    # remove headers
    arguments = arguments[1:]

    if len(arguments) != 1:
        await message.reply("Pass only one argument - date in format YYYY-MM or YYYY-MM-DD")
        return

    date_args = arguments[0].split('-')

    try:
        spendings: List[SheetSpending] = get_spendings(
            year=int(date_args[0]),
            month=int(date_args[1]),
            day=int(date_args[2]) if len(date_args) == 3 else None)
    except ValueError as e:
        await message.reply(str(e))
        return

    content = generate_report_message(spendings)
    await message.reply(content, parse_mode='MarkdownV2')


@dp.message()
async def add_spending(message: types.Message):
    print(f"Adding spendings for message: {message}")
    try:
        spendings = message.text.split('|')
        spendings = [Spending.from_string(s.strip()) for s in spendings]
    except ValueError as e:
        await message.reply(str(e))
        return
    for s in spendings:
        add_spending_spreadsheet(s)
    await message.reply(f"Spendings added, count: {len(spendings)}")


async def run_bot():
    await bot.set_my_commands(BOT_COMMANDS)
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_bot())
