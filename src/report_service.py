from collections import defaultdict
from io import BytesIO
from typing import List, Optional, Tuple

import pygal
from aiogram.utils.formatting import Bold, as_key_value, as_list, as_marked_section
# from matplotlib import pyplot as plt
from src.finances import SheetSpending
from src.spreadsheets import get_spendings


class ReportService:
    @staticmethod
    def generate_pie(percentages: List[float], categories: List[str]) -> BytesIO:
        sorted_categories = [
            categ for _, categ in sorted(zip(percentages, categories), reverse=True)
        ]
        sorted_percentages = sorted(percentages, reverse=True)
        # TODO FIX THIS
        # DETA DONT ACCEPT PYGAL, because editional sytem packages required
        # DETA DONT ACCEPT MATHPLOTLIB, because it is veryheavy ~150-200mb
        # ------------
        # pie_chart = pygal.Pie(inner_radius=.4)
        # pie_chart.title = 'Spendings by Category in Percentages'
        #
        # for percentage, category in zip(sorted_percentages, sorted_categories):
        #     pie_chart.add(f"{category} {round(percentage, 1)}%", percentage)
        #
        # # Render the pie chart to a BytesIO object
        # buf = BytesIO()
        # pie_chart.render_to_png(buf)
        # buf.seek(0)
        # ------------
        # sorted_categories = [
        #     categ for _, categ in sorted(zip(percentages, categories), reverse=True)
        # ]
        # sorted_percentages = sorted(percentages, reverse=True)
        #
        # # Create a pie chart
        # plt.figure(figsize=(10, 10))
        #
        # chart_rotation = 140
        #
        # plt.pie(
        #     sorted_percentages,
        #     labels=sorted_categories,
        #     autopct="%1.1f%%",  # noqa:WPS323
        #     startangle=chart_rotation,
        # )
        #
        # # Improve legibility by moving the legend outside the plot
        # plt.legend(
        #     sorted_categories,
        #     title="Categories",
        #     loc="center left",
        #     bbox_to_anchor=(1, 0, 0.5, 1),
        # )
        #
        # plt.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.
        # plt.title("Spendings by Category in Percentages")
        #
        # # Save plot to a BytesIO object and reset buffer position to the beginning
        # buf = BytesIO()
        # plt.savefig(buf, format="png", bbox_inches="tight")
        # buf.seek(0)
        #
        return None

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
