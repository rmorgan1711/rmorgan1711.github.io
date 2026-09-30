"""Prepare an official school calendar export for Outlook.

Usage: python prepare_outlook_calendar.py school_calendar_1558.ics
"""

from __future__ import annotations

import argparse
from datetime import date, datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

from icalendar import Calendar


TIMEZONE_NAME = "America/Denver"
DENVER = ZoneInfo(TIMEZONE_NAME)
DESCRIPTION = "Reference Sycamore for updates."


def _text(value: object) -> str:
    if value is None:
        return ""
    return str(value)


def _is_out_of_office(event: object) -> bool:
    categories = _text(event.get("CATEGORIES")).upper()
    summary = _text(event.get("SUMMARY")).upper()
    return any(
        marker in categories or marker in summary
        for marker in ("NO SCHOOL", "NOON DISMISSAL")
    )


def _start_sort_key(event: object) -> tuple[date, time, str]:
    start = event.decoded("DTSTART")
    if isinstance(start, datetime):
        start_date = start.date()
        start_time = start.timetz().replace(tzinfo=None)
    elif isinstance(start, date):
        start_date = start
        start_time = time.min
    else:
        raise ValueError(f"Unsupported DTSTART value: {start!r}")

    return start_date, start_time, _text(event.get("SUMMARY")).casefold()


def prepare_calendar(source: Path, destination: Path) -> tuple[int, int]:
    """Convert an official export and return (event count, OOO count)."""
    if source.resolve() == destination.resolve():
        raise ValueError("Input and output paths must be different.")

    calendar = Calendar.from_ical(source.read_bytes())
    events = [component for component in calendar.subcomponents if component.name == "VEVENT"]
    if not events:
        raise ValueError(f"No VEVENT components found in {source}.")

    out_of_office_count = 0
    for event in events:
        if "DTSTART" not in event or "SUMMARY" not in event:
            raise ValueError("Every VEVENT must have DTSTART and SUMMARY properties.")

        start = event.decoded("DTSTART")
        if not isinstance(start, (date, datetime)):
            raise ValueError(f"Unsupported DTSTART value: {start!r}")

        categories = _text(event.get("CATEGORIES")).upper()
        is_noon_dismissal = "NOON DISMISSAL" in categories or "NOON DISMISSAL" in _text(
            event.get("SUMMARY")
        ).upper()
        if is_noon_dismissal and isinstance(start, date) and not isinstance(start, datetime):
            del event["DTSTART"]
            del event["DTEND"]
            event.add("DTSTART", datetime.combine(start, time(11), tzinfo=DENVER))
            event.add("DTEND", datetime.combine(start, time(17), tzinfo=DENVER))
            start = event.decoded("DTSTART")

        is_all_day = isinstance(start, date) and not isinstance(start, datetime)
        is_out_of_office = _is_out_of_office(event)
        event["CATEGORIES"] = "kids"
        event["DESCRIPTION"] = DESCRIPTION
        event["STATUS"] = "CONFIRMED"
        event["TRANSP"] = "OPAQUE" if is_out_of_office else "TRANSPARENT"
        event["X-MICROSOFT-CDO-BUSYSTATUS"] = (
            "OOF" if is_out_of_office else "FREE"
        )
        event["X-MICROSOFT-CDO-ALLDAYEVENT"] = "TRUE" if is_all_day else "FALSE"
        out_of_office_count += int(is_out_of_office)

    ordered_events = sorted(events, key=_start_sort_key)
    event_iterator = iter(ordered_events)
    calendar.subcomponents[:] = [
        next(event_iterator) if component.name == "VEVENT" else component
        for component in calendar.subcomponents
    ]

    calendar["PRODID"] = "-//Custom Excel Calendar//EN"
    calendar["METHOD"] = "PUBLISH"
    calendar["X-WR-TIMEZONE"] = TIMEZONE_NAME

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(calendar.to_ical())
    return len(events), out_of_office_count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Official school calendar .ics export")
    parser.add_argument(
        "output",
        nargs="?",
        type=Path,
        help="Output path (defaults to <input>_outlook.ics)",
    )
    args = parser.parse_args()
    output = args.output or args.input.with_name(f"{args.input.stem}_outlook.ics")
    event_count, out_of_office_count = prepare_calendar(args.input, output)
    print(
        f"Processed {event_count} events: {out_of_office_count} OOO, "
        f"{event_count - out_of_office_count} free. Wrote {output}."
    )


if __name__ == "__main__":
    main()