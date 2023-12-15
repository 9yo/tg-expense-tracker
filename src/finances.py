from datetime import date
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field

from src.currency_converter import CurrencyConverter


class Spending(BaseModel):
    name: str = Field(..., description="Name")
    category: str = Field(..., description="Category")
    description: str = Field(..., description="Description")
    cost: float = Field(..., description="Cost")  # Assuming cost is a float
    currency: Literal["USD", "RUB", "GEL", "EUR", "TRY", "AMD"] = Field(
        ...,
        description="Currency",
    )
    source: Literal["Cash", "Card", "Bank", "Crypto"] = Field(..., description="Source")
    datetime: date = Field(..., description="Date")  # Changed to date type

    @classmethod
    def from_list(cls, list_: List[Any]) -> "Spending":
        return cls(
            name=list_[0],
            category=list_[1],
            description=list_[2],
            cost=float(list_[3].replace(",", ".")),
            currency=list_[4],
            source=list_[5],
            datetime=date.fromisoformat(
                list_[6],
            ),  # Assumes date in ISO format (YYYY-MM-DD)
        )

    @classmethod
    def from_string(cls, string: str) -> "Spending":  # noqa: WPS210
        try:  # noqa: WPS229
            spending_args = [
                el.strip().replace("\n", "") for el in string.split(";")
            ]  # noqa: WPS221
            (  # noqa: WPS236
                name,
                cost,
                category,
                description,
                currency,
                source,
                date_str,
            ) = spending_args
            return cls(
                name=name.strip().replace("\n", ""),
                cost=float(cost.strip().replace(",", ".").replace("\n", "")),
                category=category,
                description=description,
                currency=currency,  # type: ignore
                source=source,  # type: ignore
                datetime=date.fromisoformat(
                    date_str,
                ),  # Assumes date in ISO format (YYYY-MM-DD)
            )
        except ValueError as err:
            raise ValueError(
                "Invalid spending format. "
                "Expected format: "  # noqa: WPS326
                "name;cost;category;description;currency;source;date",  # noqa: WPS326
            ) from err

    @classmethod
    def generate_string_schema(cls) -> str:
        fields = cls.model_fields
        field_descriptions = [
            f"{value.description} {value.annotation}; \n"
            for _, value in fields.items()  # noqa: WPS202, WPS110
        ]
        return "".join(field_descriptions)


class SheetSpending(Spending):
    usd: Optional[float] = Field(..., description="Common currency (USD) cost")

    @classmethod
    def from_list(cls, list_: List[Any]) -> "SheetSpending":
        cost = float(list_[3].replace(",", "."))
        currency = list_[4]
        try:
            usd: float = float(list_[7].replace(",", "."))
        except IndexError:
            usd = CurrencyConverter.convert(
                amount=cost,
                from_currency=currency,
                to_currency="USD",
            )
        return cls(
            name=list_[0],
            category=list_[1],
            description=list_[2],
            cost=cost,
            currency=currency,
            source=list_[5],
            datetime=date.fromisoformat(
                list_[6],
            ),  # Assumes date in ISO format (YYYY-MM-DD)
            usd=usd,
        )

    @classmethod
    def from_spending(cls, spending: Spending) -> "SheetSpending":
        usd_amount: Optional[float] = None

        if spending.currency == "USD":
            usd_amount = spending.cost

        else:
            usd_amount = CurrencyConverter.convert(
                amount=spending.cost,
                from_currency=spending.currency,
                to_currency="USD",
            )

        return cls(
            name=spending.name,
            category=spending.category,
            description=spending.description,
            cost=spending.cost,
            currency=spending.currency,
            source=spending.source,
            datetime=spending.datetime,
            usd=usd_amount,
        )
