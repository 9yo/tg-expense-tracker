import requests
from aiogram import types
from fastapi import FastAPI, Request

from src.bot import dp, bot, BOT_URL
from src.settings import WEBHOOK_HOST

app = FastAPI()


@app.post('/webhook')
async def get_telegram_update(request: Request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return {'success': True}


@app.get("/set_webhook")
def url_setter():
    set_url = f"{BOT_URL}/setWebHook?url=https://{WEBHOOK_HOST}/webhook"
    resp = requests.get(set_url)
    return resp.json()
