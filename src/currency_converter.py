import functools
import json
import logging
from typing import Any, Dict

import google_currency

logger = logging.getLogger(__name__)


class CurrencyConverter:
    """Currency converter class."""

    @classmethod
    @functools.lru_cache(maxsize=10)
    def get_rate(cls, from_currency: str, to_currency: str) -> float:  # noqa: C901
        """Get rate from a currency to another."""
        if from_currency == to_currency:
            return 1.0

        resp: str = google_currency.convert(from_currency, to_currency, 1)
        try:
            resp_json: Dict[str, Any] = json.loads(resp)
        except json.JSONDecodeError as err:
            logger.error(
                f"Unable to convert from {from_currency} to {to_currency}",
                err,
            )
            return 0
        try:
            rate = float(resp_json["amount"])
        except KeyError as err:  # ignore:WPS440
            logger.error(
                f"Unable to convert from {from_currency} to {to_currency}",
                err,
                resp,
            )
            return 0
        except ValueError as err:  # ignore:WPS440
            logger.error(
                f"Unable to convert from {from_currency} to {to_currency}",
                err,
                resp,
            )
            return 0
        logger.info(f"Converted {from_currency} to {to_currency} with rate {rate}")
        return rate

    @classmethod
    def convert(cls, from_currency: str, to_currency: str, amount: float) -> float:
        """Convert from one currency to another."""
        return amount * cls.get_rate(from_currency, to_currency)
