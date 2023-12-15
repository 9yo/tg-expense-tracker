from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from src.bot.filters import CustomFilter
from src.bot.forms.report import ReportFrom
from src.bot.reply import safe_replay
from src.keyboard_service import (
    SHOW_REPORT,
    generate_datetime_keyboard,
    start_keyboard,
)
from src.report_service import ReportService

router = Router()


@router.message(CustomFilter(SHOW_REPORT))
async def get_report_with_keyboard(message: types.Message, state: FSMContext) -> None:
    """
    Add a spending record.

    Args:
        message (types.Message): The message object containing the spending data.
    """
    await state.set_state(ReportFrom.datetime)

    await safe_replay(
        message,
        text="Enter spending name",
        keyboard=generate_datetime_keyboard(days=False),
    )


@router.message(ReportFrom.datetime)
async def add_spending_name(message: types.Message, state: FSMContext) -> None:
    if not message.text:
        await state.clear()
        await message.answer(
            "No data provided",
            reply_markup=start_keyboard,
        )
        return

    report, photo = ReportService.generate_report(*message.text.split("-"))
    await safe_replay(
        message,
        photo=photo,
        caption=report,
        text=report,
        parse_mode="MarkdownV2",
        keyboard=start_keyboard,
    )
