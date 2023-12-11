"""FastAPI server for webhook."""
import logging
from json import JSONDecodeError
from typing import Any, Dict

import requests
from aiogram import types
from fastapi import FastAPI, Request
from src.bot import bot, bot_url, dp
from src.settings import WEBHOOK_HOST

app = FastAPI()


@app.post("/webhook")
async def get_telegram_update(request: Request) -> Dict[str, bool]:
    """Get update from Telegram.

    Args:
        request (Request): The request object.

    Returns:
        dict: A success status.
    """
    try:
        request_data = await request.json()
    except JSONDecodeError as err:
        logging.error(f"Invalid request data from Telegram!!!, {err}")
        # HOT FIX: Telegram sends empty updates sometimes or invalid JSON
        return {"success": True}
    update = types.Update(**request_data)
    await dp.feed_update(bot, update)
    return {"success": True}


@app.get("/set_webhook")
def url_setter() -> Dict[Any, Any]:
    """Set webhook URL.

    Returns:
        dict: The response from the webhook URL setup.
    """

    set_url: str = f"{bot_url}/setWebHook?url=https://{WEBHOOK_HOST}"
    set_url = f"{set_url}/webhook"
    set_url = f"{set_url}?drop_pending_updates=True"

    resp = requests.get(set_url, timeout=10)  # Added a timeout
    return resp.json()
