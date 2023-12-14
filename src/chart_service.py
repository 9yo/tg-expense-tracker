from io import BytesIO
from typing import List, Tuple

from requests import Response, post
from src.settings import CHART_SERVICE_RESPONSE_TIMEOUT, CHART_SERVICE_URL

DEFAULT_BB_TO_ANCHOR = (1, 0, 0.5, 1)


class ChartService:
    @staticmethod
    def pie(  # noqa:WPS211
        chart_values: List[float],
        labels: List[str],
        figsize: Tuple[int, int] = (10, 10),
        chart_rotation: int = 140,
        title: str = "Title",
        legend_title: str = "Legend Title",
        legend_loc: str = "center left",
        bbox_to_anchor: Tuple[float, float, float, float] = DEFAULT_BB_TO_ANCHOR,
        autopct: str = "%1.1f%%",
    ) -> BytesIO:
        pie: Response = post(
            url=CHART_SERVICE_URL + "/pie",
            json={
                "chart_values": chart_values,
                "labels": labels,
                "figsize": figsize,
                "chart_rotation": chart_rotation,
                "title": title,
                "legend_title": legend_title,
                "legend_loc": legend_loc,
                "bbox_to_anchor": bbox_to_anchor,
                "autopct": autopct,
            },
            stream=True,
            timeout=CHART_SERVICE_RESPONSE_TIMEOUT,
        )
        return BytesIO(pie.content)
