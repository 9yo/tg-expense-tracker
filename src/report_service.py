from collections import defaultdict
from io import BytesIO
from typing import List, Optional, Tuple

from aiogram.utils.formatting import Bold, as_key_value, as_list, as_marked_section
from src.chart_service import ChartService
from src.finances import SheetSpending
from src.spreadsheets import get_spendings


class ReportService:
    @staticmethod
    def generate_pie(percentages: List[float], categories: List[str]) -> BytesIO:
        sorted_categories = [
            categ for _, categ in sorted(zip(percentages, categories), reverse=True)
        ]
        sorted_percentages = sorted(percentages, reverse=True)

        return ChartService.pie(
            chart_values=sorted_percentages,
            labels=sorted_categories,
            title="Total spendings by category",
            legend_title="Categories",
            legend_loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
            autopct="%1.1f%%",
        )

    @classmethod
    def generate_report(  # noqa:WPS210
        cls,
        year: str,
        month: str,
        day: Optional[str] = None,
    ) -> Tuple[str, BytesIO]:
        """
        Generate a report message from a list of spendings.

        Args:
            year (str): The year to generate the report for.
            month (str): The month to generate the report for.
            day (str): The day to generate the report for.
        Returns:
            str: Formatted report message.
        """
        spendings: List[SheetSpending] = get_spendings(
            year=int(year),
            month=int(month),
            day=int(day) if day else None,
        )

        spendings_by_category: defaultdict[str, float] = defaultdict(float)
        total_spendings: float = 0
        for spending in spendings:
            total_spendings += spending.usd or 0
            spendings_by_category[spending.category] += spending.usd or 0

        categories = list(spendings_by_category.keys())
        percentages = [
            value / total_spendings * 100
            for category, value in spendings_by_category.items()
        ]

        if not spendings:
            return "No spendings found", BytesIO()

        text = as_list(
            as_marked_section(
                Bold("Total spendings by category"),
                *[
                    as_key_value(category, round(cost, 2))
                    for category, cost in spendings_by_category.items()
                ],
            ),
            as_marked_section(
                Bold("Summary:"),
                as_key_value("Total spendings", round(total_spendings, 2)),
                as_key_value("Total spendings records", len(spendings)),
                as_key_value(
                    "Total days found",
                    len({spnd.datetime.day for spnd in spendings}),
                ),
            ),
            sep="\n\n",
        ).as_markdown()

        pie = cls.generate_pie(percentages, categories)

        return text, pie
