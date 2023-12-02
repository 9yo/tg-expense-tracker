"""Test bot."""
import pytest
from httpx import AsyncClient
from main import app
from starlette.status import HTTP_200_OK


@pytest.mark.asyncio
async def test_webhook() -> None:
    """Test webhook."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/webhook/test_token",
            json={"update_id": 1, "message": {}},
        )
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"error": "Invalid token"}
