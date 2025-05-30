from .second import SecondStrategy
from .minute import MinuteStrategy
from .hour import HourStrategy
from .day import DayStrategy
from .week import WeekStrategy
from typing import Literal


STRATEGY_MAP = {
    "second": SecondStrategy(),
    "minute": MinuteStrategy(),
    "hour": HourStrategy(),
    "day": DayStrategy(),
    "week": WeekStrategy(),
}


def get_calculation_strategy(
    period: Literal["second", "minute", "hour", "day", "week", "month", "jmonth"],
):
    return STRATEGY_MAP[period]
