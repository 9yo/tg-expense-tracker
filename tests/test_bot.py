import pytest
from httpx import AsyncClient

from main import app


@pytest.mark.asyncio
async def test_webhook():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/webhook/test_token", json={"update_id": 1, "message": {}})
    assert response.status_code == 200
    assert response.json() == {"error": "Invalid token"}
