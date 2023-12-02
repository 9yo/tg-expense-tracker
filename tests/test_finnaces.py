"""Test finances module."""
from datetime import date

import pytest
from src.finances import Spending  # Replace with the actual import


def test_spending_from_string() -> None:
    """Test spending from string."""
    spending_year = 2021
    spending_month = 11
    spending_day = 1

    spending_cost = 10.5

    spending = Spending.from_string(
        f"Lunch;{spending_cost};Food;Nice meal;USD;Cash;"
        + f"{spending_year}-{spending_month}-{spending_day}",
    )

    assert spending.name == "Lunch"
    assert spending.cost == spending_cost
    assert spending.currency == "USD"
    assert spending.source == "Cash"
    assert spending.datetime == date(
        year=spending_year,
        month=spending_month,
        day=spending_day,
    )

    spending = Spending.from_string("dfsd;10.5;Рестораны;Классно;GEL;Card;2023-11-02")
    spending = Spending.from_string(
        "sadfsd asd;103234.512;Продукты;111;RUB;Cash;2023-11-03",
    )


def test_invalid_spending_string() -> None:
    """Test invalid spending string."""
    with pytest.raises(ValueError):
        Spending.from_string("Invalid;String")


# Additional tests can be added here
