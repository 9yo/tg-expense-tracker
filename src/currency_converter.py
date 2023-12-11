import functools
import json
import logging

import google_currency

logger = logging.getLogger(__name__)


class CurrencyConverter:
    """Currency converter class."""

    @classmethod
    @functools.lru_cache(maxsize=10)
    def get_rate(cls, from_currency: str, to_currency: str) -> float:
        """Get rate from a currency to another."""
        if from_currency == to_currency:
            return 1.0

        rate: float = 0.0
        resp: str = google_currency.convert(from_currency, to_currency, 1)
        try:
            resp = json.loads(resp)
        except json.JSONDecodeError as err:
            logger.error(
                f"Unable to convert from {from_currency} to {to_currency}", err
            )
            return rate
        try:
            rate = float(resp["amount"])
        except (KeyError, TypeError, ValueError) as err:
            logger.error(
                f"Unable to convert from {from_currency} to {to_currency}", err, resp
            )
        logger.info(f"Converted {from_currency} to {to_currency} with rate {rate}")
        return rate

    @classmethod
    def convert(cls, from_currency: str, to_currency: str, amount: float) -> float:
        """Convert from one currency to another."""
        return amount * cls.get_rate(from_currency, to_currency)
