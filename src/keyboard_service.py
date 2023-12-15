from datetime import datetime, timedelta
from typing import List

from aiogram import types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from google_currency import CODES
from src.spreadsheets import get_categories

ADD_SPENDING = "Add spending"
SHOW_REPORT = "Show Report"

SPENDING_SOURCES: List[str] = ["Cash", "Card", "Crypto"]

CANCEL_COMMAND = "Cancel"
CONFIRM_COMMAND = "Confirm"

start_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=ADD_SPENDING)], [KeyboardButton(text=SHOW_REPORT)]],
    resize_keyboard=True,  # Resizes the keyboard to the size of its buttons
    one_time_keyboard=True,  # Hides the keyboard after a button is pressed
)

categories = get_categories()

categories_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=category)] for category in categories],
    resize_keyboard=True,
    one_time_keyboard=True,
)

currencies = CODES.keys()
currencies_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=currency)] for currency in currencies],
    resize_keyboard=True,
    one_time_keyboard=True,
)

spending_sources_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=source)] for source in SPENDING_SOURCES],
    resize_keyboard=True,
    one_time_keyboard=True,
)

confirmation_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=CONFIRM_COMMAND)],
        [KeyboardButton(text=CANCEL_COMMAND)],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)


def is_confirmed(message: types.Message) -> bool:
    return message.text == CONFIRM_COMMAND


def generate_confirm_keyboard(**kwargs) -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text=f"{k}: {v}")] for k, v in kwargs.items()]
    keyboard.append([KeyboardButton(text=CONFIRM_COMMAND)])
    keyboard.append([KeyboardButton(text=CANCEL_COMMAND)])
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
        **kwargs,
    )


def generate_datetime_keyboard() -> ReplyKeyboardMarkup:
    today = datetime.today()
    dates = [
        today,
        today - timedelta(days=1),
        today - timedelta(days=2),
    ]
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=date.strftime("%Y-%m-%d"))] for date in dates],
    )
