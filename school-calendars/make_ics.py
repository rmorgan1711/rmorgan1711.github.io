from pathlib import Path
from datetime import timezone
from zoneinfo import ZoneInfo
import pandas as pd
import uuid

INPUT_XLSX = "CK Calendar 2026-27.xlsx"
OUTPUT_ICS = "CK Calendar 2026-27.ics"

DENVER = ZoneInfo("America/Denver")


def utc_string(dt):
    return (
        dt.replace(tzinfo=DENVER)
        .astimezone(timezone.utc)
        .strftime("%Y%m%dT%H%M%SZ")
    )


df = pd.read_excel(INPUT_XLSX)

lines = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//Custom Excel Calendar//EN",
    "CALSCALE:GREGORIAN",
    "METHOD:PUBLISH",
    "X-WR-TIMEZONE:America/Denver",
]

for _, row in df.iterrows():

    uid = row["UID"]

    if pd.isna(uid) or str(uid).strip() == "":
        uid = str(uuid.uuid4())

    lines.extend([
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"SUMMARY:{row['SUMMARY']}",
        f"DESCRIPTION:{row.get('DESCRIPTION','')}",
        f"CATEGORIES:{row.get('CATEGORIES','')}",
        f"STATUS:{row.get('STATUS','CONFIRMED')}",
        f"TRANSP:{row.get('TRANSP','OPAQUE')}",
        f"X-MICROSOFT-CDO-BUSYSTATUS:{row.get('X-MICROSOFT-CDO-BUSYSTATUS','OOF')}",
    ])

    all_day = str(row["X-MICROSOFT-CDO-ALLDAYEVENT"]).upper() == "TRUE"

    if all_day:

        start = pd.to_datetime(row["DTSTART"]).strftime("%Y%m%d")
        end = pd.to_datetime(row["DTEND"]).strftime("%Y%m%d")

        lines.extend([
            "X-MICROSOFT-CDO-ALLDAYEVENT:TRUE",
            f"DTSTART;VALUE=DATE:{start}",
            f"DTEND;VALUE=DATE:{end}",
        ])

    else:

        start = pd.to_datetime(row["DTSTART"])
        end = pd.to_datetime(row["DTEND"])

        tzid = row.get("TZID", "America/Denver")

        lines.extend([
            "X-MICROSOFT-CDO-ALLDAYEVENT:FALSE",
            f"DTSTART;TZID={tzid}:{start.strftime('%Y%m%dT%H%M%S')}",
            f"DTEND;TZID={tzid}:{end.strftime('%Y%m%dT%H%M%S')}",
        ])

    #
    # Reminder 1
    #
    if not pd.isna(row.get("VALARM1.TRIGGER")):

        reminder = pd.to_datetime(row["VALARM1.TRIGGER"])

        lines.extend([
            "BEGIN:VALARM",
            "ACTION:DISPLAY",
            f"DESCRIPTION:{row['SUMMARY']}",
            f"TRIGGER;VALUE=DATE-TIME:{utc_string(reminder)}",
            "END:VALARM",
        ])

    #
    # Reminder 2
    #
    if not pd.isna(row.get("VALARM2.TRIGGER")):

        reminder = pd.to_datetime(row["VALARM2.TRIGGER"])

        lines.extend([
            "BEGIN:VALARM",
            "ACTION:DISPLAY",
            f"DESCRIPTION:{row['SUMMARY']}",
            f"TRIGGER;VALUE=DATE-TIME:{utc_string(reminder)}",
            "END:VALARM",
        ])

    lines.append("END:VEVENT")

lines.append("END:VCALENDAR")

Path(OUTPUT_ICS).write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8"
)

print("Created:", OUTPUT_ICS)
