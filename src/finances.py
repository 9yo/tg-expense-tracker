import json
from datetime import date
from typing import Literal, Optional

import google_currency
from pydantic import BaseModel, Field


class Spending(BaseModel):
    name: str = Field(..., description="Name")
    category: str = Field(..., description="Category")
    description: str = Field(..., description="Description")
    cost: float = Field(..., description="Cost")  # Assuming cost is a float
    currency: Literal['USD', 'RUB', 'GEL', 'EUR', 'TRY', 'AMD'] = Field(..., description="Currency")
    source: Literal['Cash', 'Card', 'Bank', 'Crypto'] = Field(..., description="Source")
    datetime: date = Field(..., description="Date")  # Changed to date type

    @staticmethod
    def from_list(list_: list) -> "Spending":
        return Spending(
            name=list_[0],
            category=list_[1],
            description=list_[2],
            cost=float(list_[3].replace(',', '.')),
            currency=list_[4],
            source=list_[5],
            datetime=date.fromisoformat(list_[6])  # Assumes date in ISO format (YYYY-MM-DD)
        )

    @staticmethod
    def from_string(string: str) -> "Spending":
        try:
            spending_args = [el.strip().replace('\n', '') for el in string.split(';')]
            print(spending_args)
            name, cost, category, description, currency, source, date_str = spending_args
            return Spending(
                name=name.strip().replace('\n', ''),
                cost=float(cost.strip().replace(',', '.').replace('\n', '')),
                category=category,
                description=description,
                currency=currency,
                source=source,
                datetime=date.fromisoformat(date_str)  # Assumes date in ISO format (YYYY-MM-DD)
            )
        except ValueError as e:
            print(e)
            raise ValueError("Invalid spending format. Expected format: name;cost;category;description;currency;source;date")

    @classmethod
    def generate_string_schema(cls) -> str:
        fields = cls.model_fields
        resp = ''
        for el in fields:
            resp += f"{fields[el].description} {fields[el].annotation}; \n"
        return resp


class SheetSpending(Spending):
    usd: Optional[float] = Field(..., description="Common currency (USD) cost")

    @staticmethod
    def from_list(list_: list) -> "Spending":
        return SheetSpending(
            name=list_[0],
            category=list_[1],
            description=list_[2],
            cost=float(list_[3].replace(',', '.')),
            currency=list_[4],
            source=list_[5],
            datetime=date.fromisoformat(list_[6]),  # Assumes date in ISO format (YYYY-MM-DD)
            usd=float(list_[7].replace(',', '.')),
        )

    @staticmethod
    def from_spending(spending: Spending) -> "SheetSpending":
        usd_amount = None

        if spending.currency == 'USD':
            usd_amount = spending.cost

        else:
            usd_amount = google_currency.convert(
                amnt=spending.cost,
                currency_from=spending.currency,
                currency_to='USD'
            )
            if usd_amount:
                usd_amount = json.loads(usd_amount).get('amount', None)

        return SheetSpending(
            name=spending.name,
            category=spending.category,
            description=spending.description,
            cost=spending.cost,
            currency=spending.currency,
            source=spending.source,
            datetime=spending.datetime,
            usd=usd_amount
        )
