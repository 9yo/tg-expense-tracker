from datetime import date

import pytest

from src.finances import Spending  # Replace with the actual import


def test_spending_from_string():
    test_string = "Lunch;10.5;Food;Nice meal;USD;Cash;2021-07-15"
    spending = Spending.from_string(test_string)

    assert spending.name == "Lunch"
    assert spending.cost == 10.5
    assert spending.category == "Food"
    assert spending.description == "Nice meal"
    assert spending.currency == "USD"
    assert spending.source == "Cash"
    assert spending.datetime == date(2021, 7, 15)

    # some specific examples
    test_string = "dfsd;10.5;Рестораны;Классно;GEL;Card;2023-11-02"
    spending = Spending.from_string(test_string)
    test_string = "sadfsd asd;103234.512;Продукты;%%%;RUB;Cash;2023-11-03"
    spending = Spending.from_string(test_string)


def test_invalid_spending_string():
    with pytest.raises(ValueError):
        Spending.from_string("Invalid;String")

# Additional tests can be added here
