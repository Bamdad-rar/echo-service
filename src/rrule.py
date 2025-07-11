from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Literal, Self


FREQ = Literal["SECONDLY", "MINUTELY", "HOURLY",
               "DAILY", "WEEKLY", "MONTHLY", "YEARLY"]

# format datetimes in the UTC form RFC 5545 expects
def _fmt_until(dt: datetime) -> str:
    if dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) != timedelta(0):
        raise ValueError("UNTIL must be a UTC datetime (tz-aware, offset 0)")
    return dt.strftime("%Y%m%dT%H%M%SZ")


@dataclass
class RRuleBuilder:
    """RRULE SDK for generating RFC 5545 compliant Rready-to-persist RULE strings with timezone support.

    Provides a fluent interface to construct recurrence rules according to the
    iCalendar standard. Generates a tuple containing the RRULE string and an 
    associated IANA timezone name.

    Attributes:
        _parts: Internal storage for RRULE components
        _timezone: IANA timezone name (stored separately from RRULE)

    Example:
        >>> from datetime import datetime
        >>> from zoneinfo import ZoneInfo
        >>> utc_dt = datetime(2025, 12, 31, 22, tzinfo=ZoneInfo("UTC"))
        >>> 
        >>> rrule, tz = (
        ...     RRuleBuilder.daily()
        ...        .at(9, 0)
        ...        .interval(2)
        ...        .until(utc_dt)
        ...        .timezone("Europe/Berlin")
        ...        .build()
        ... )
        >>> print(rrule)
        FREQ=DAILY;INTERVAL=2;BYHOUR=9;BYMINUTE=0;UNTIL=20251231T220000Z
        >>> print(tz)
        Europe/Berlin

    Key Features:
    - Chainable builder pattern
    - Automatic validation of RFC 5545 constraints
    - Timezone-aware datetime handling
    - Ordered component output for compatibility

    Note:
    - The `timezone` is stored separately from the RRULE string as required by RFC 5545
    - All datetime parameters for `until()` must be UTC-aware with zero offset
    - Methods modifying mutually exclusive parameters (COUNT/UNTIL) auto-clear conflicts
    """
    _parts: dict[str, str] = field(default_factory=dict)
    _timezone: str | None = None # IANA/Olson name, *not* in the RRULE

    def freq(self, value: FREQ) -> Self:
        self._parts["FREQ"] = value
        return self

    @classmethod
    def secondly(cls) -> Self: return cls().freq("SECONDLY")
    @classmethod
    def minutely(cls) -> Self: return cls().freq("MINUTELY")
    @classmethod
    def hourly  (cls) -> Self: return cls().freq("HOURLY")
    @classmethod
    def daily   (cls) -> Self: return cls().freq("DAILY")
    @classmethod
    def weekly  (cls) -> Self: return cls().freq("WEEKLY")
    @classmethod
    def monthly (cls) -> Self: return cls().freq("MONTHLY")
    @classmethod
    def yearly  (cls) -> Self: return cls().freq("YEARLY")

    def interval(self, n: int) -> Self:
        if n < 1:
            raise ValueError("INTERVAL must be ≥ 1")
        self._parts["INTERVAL"] = str(n)
        return self

    def count(self, n: int) -> Self:
        if n < 1:
            raise ValueError("COUNT must be ≥ 1")
        self._parts["COUNT"] = str(n)
        # NB: mutually exclusive with UNTIL (RFC 5545 §3.8.5.3)
        self._parts.pop("UNTIL", None)
        return self

    def until(self, dt: datetime) -> Self:
        self._parts["UNTIL"] = _fmt_until(dt)
        self._parts.pop("COUNT", None)
        return self

    def by_second(self, *seconds: int) -> Self:
        self._parts["BYSECOND"] = ",".join(map(str, seconds)); return self

    def by_minute(self, *minutes: int) -> Self:
        self._parts["BYMINUTE"] = ",".join(map(str, minutes)); return self

    def by_hour(self, *hours: int) -> Self:
        self._parts["BYHOUR"] = ",".join(map(str, hours)); return self

    # Weekdays: “MO”, “TU”, … ; pass strings or `dateutil.rrule.MO`, etc.
    def by_weekday(self, *days: str | int) -> Self:
        formatted = []
        for d in days:
            formatted.append(str(d) if isinstance(d, int) else d.upper()[:2])
        self._parts["BYDAY"] = ",".join(formatted)
        return self

    def by_monthday(self, *days: int) -> Self:
        self._parts["BYMONTHDAY"] = ",".join(map(str, days)); return self

    def by_month(self, *months: int) -> Self:
        self._parts["BYMONTH"] = ",".join(map(str, months)); return self

    def at(self, hour: int, minute: int = 0, second: int = 0) -> Self:
        """Shortcut for BYHOUR / BYMINUTE / BYSECOND"""
        return self.by_hour(hour).by_minute(minute).by_second(second)

    def timezone(self, tz_name: str) -> Self:
        """
        Attach an IANA zone name – *not* inside the RRULE string.
        Keep it alongside the rule when you persist the schedule.
        """
        self._timezone = tz_name
        return self

    def build(self) -> tuple[str, str | None]:
        """Return `(rrule_string, timezone_or_None)`."""
        if "FREQ" not in self._parts:
            raise ValueError("RRULE must contain FREQ")
        # RFC 5545 requires UNTIL *or* COUNT (optional) – not both
        if "UNTIL" in self._parts and "COUNT" in self._parts:
            raise ValueError("RRULE can’t have both COUNT and UNTIL")
        # Older generators like Outlook care about field order → sort by spec
        ordering = ("FREQ", "INTERVAL", "BYSECOND", "BYMINUTE", "BYHOUR",
                    "BYDAY", "BYMONTHDAY", "BYMONTH", "COUNT", "UNTIL")
        ordered = [f"{k}={self._parts[k]}" for k in ordering if k in self._parts]
        return ";".join(ordered), self._timezone

    def __str__(self) -> str:
        return self.build()[0]

