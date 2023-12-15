import logging

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from src.bot.filters import CustomFilter
from src.bot.reply import safe_replay
from src.finances import Spending, SpendingForm
from src.keyboard_service import (
    ADD_SPENDING,
    CANCEL_COMMAND,
    CONFIRM_COMMAND,
    categories_keyboard,
    currencies_keyboard,
    generate_confirm_keyboard,
    generate_datetime_keyboard,
    spending_sources_keyboard,
    start_keyboard,
)
from src.spreadsheets import add_spending as add_spending_spreadsheet

router = Router()


@router.message(CustomFilter(ADD_SPENDING))
async def add_spending_with_keyboard(message: types.Message, state: FSMContext) -> None:
    """
    Add a spending record.

    Args:
        message (types.Message): The message object containing the spending data.
    """
    await state.set_state(SpendingForm.name)

    await safe_replay(
        message,
        text="Enter spending name",
        keyboard=ReplyKeyboardRemove(),
    )


@router.message(SpendingForm.name)
async def add_spending_name(message: types.Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(SpendingForm.category)
    await safe_replay(
        message,
        text="Chose from category, or enter your own",
        keyboard=categories_keyboard,
    )


@router.message(SpendingForm.category)
async def add_spending_category(message: types.Message, state: FSMContext) -> None:
    await state.update_data(category=message.text)
    await state.set_state(SpendingForm.description)
    await safe_replay(message, text="Enter spending description")


@router.message(SpendingForm.description)
async def add_spending_description(message: types.Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(SpendingForm.cost)
    await safe_replay(message, text="Enter spending cost")


@router.message(SpendingForm.cost)
async def add_spending_cost(message: types.Message, state: FSMContext) -> None:
    await state.update_data(cost=message.text)
    await state.set_state(SpendingForm.currency)
    await safe_replay(
        message,
        text="Enter spending currency",
        keyboard=currencies_keyboard,
    )


@router.message(SpendingForm.currency)
async def add_spending_currency(message: types.Message, state: FSMContext) -> None:
    await state.update_data(currency=message.text)
    await state.set_state(SpendingForm.source)
    await safe_replay(
        message,
        text="Enter spending source",
        keyboard=spending_sources_keyboard,
    )


@router.message(SpendingForm.source)
async def add_spending_source(message: types.Message, state: FSMContext) -> None:
    await state.update_data(source=message.text)
    await state.set_state(SpendingForm.datetime)
    await safe_replay(
        message,
        text="Enter spending date in format YYYY-MM-DD",
        keyboard=generate_datetime_keyboard(),
    )


@router.message(SpendingForm.datetime)
async def add_spending_datetime(message: types.Message, state: FSMContext) -> None:
    await state.update_data(datetime=message.text)
    await state.set_state(SpendingForm.confirmation)
    await safe_replay(
        message,
        text=f"Confirm spending:",
        keyboard=generate_confirm_keyboard(**await state.get_data()),
    )


@router.message(SpendingForm.confirmation)
async def add_spending_confirmation(message: types.Message, state: FSMContext) -> None:
    await state.update_data(confirmation=message.text)

    if message.text == CANCEL_COMMAND:
        current_state = await state.get_state()
        if current_state is None:
            return

        logging.info("Cancelling state %r", current_state)
        await state.clear()
        await message.answer(
            "Cancelled.",
            reply_markup=ReplyKeyboardRemove(),
        )

    elif message.text == CONFIRM_COMMAND:
        data = await state.get_data()
        try:
            spending = Spending(**data)
        except TypeError as err:
            logging.error(err)
            await safe_replay(
                message,
                text=f"Error: {err}",
                keyboard=start_keyboard,
            )
            return
        add_spending_spreadsheet([spending])
        await safe_replay(
            message,
            f"Spendings added, count: 1",  # noqa:WPS237
            keyboard=start_keyboard,
        )
    else:
        if ":" not in message.text:
            await safe_replay(
                message,
                text=f"Confirm spending:",
                keyboard=generate_confirm_keyboard(**await state.get_data()),
            )
            return

        for key, value in (await state.get_data()).items():
            if key in message.text:
                await state.set_state(getattr(SpendingForm, key))
                await safe_replay(
                    message,
                    text=f"Editing {key}: {value}",
                    keyboard=ReplyKeyboardRemove(),
                )
                return
