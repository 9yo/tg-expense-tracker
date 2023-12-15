import logging
from io import BytesIO
from typing import Any, Optional

from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BufferedInputFile, ReplyKeyboardMarkup


async def safe_replay(
    message: types.Message,
    *args: Any,
    photo: Optional[BytesIO] = None,
    keyboard: Optional[ReplyKeyboardMarkup] = None,
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
            await message.reply(*args, reply_markup=keyboard, **kwargs)
    except TelegramBadRequest as err:
        logging.info("Replay not achieved, reason: TelegramBadRequest", err)
