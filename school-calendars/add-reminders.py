import icalendar
from icalendar import Calendar, Event, Alarm, Timezone, TimezoneStandard, TimezoneDaylight
from datetime import timedelta, datetime
from pathlib import Path
import csv
import zoneinfo
import uuid


def hours_to_human_desc(description: str, hours: int) -> str:
    """Convert hours to a human-readable string in days and hours."""
    days = int(hours) // 24
    hrs = int(hours) % 24
    result = []
    if days > 0:
        result = f"{days} day{'s' if days != 1 else ''} "
        if hrs > 0:
            result += f"{hrs} hour{'s' if hrs != 1 else ''} "
        result += f"to {description}"
    else:
        result = f"{hrs} hour{'s' if hrs != 1 else ''} "
        result += f"to {description}"

    return result
    

cal_out_path = Path("./St Ann School Calendar.ics")

data_path = Path("./St Ann School Calendar curated.csv")
event_data = []
with open(data_path, 'r') as f:
    csv_dict_reader = csv.DictReader(f)
    for row in csv_dict_reader:
        event_data.append(row)

CT = zoneinfo.ZoneInfo("America/Chicago")
date_fmt = "%m/%d/%Y"
time_fmt = "%I:%M %p"

cal = Calendar()
cal.add("prodid", "-//Microsoft Corporation//Outlook 16.0 MIMEDIR//EN")
cal.add("version", "2.0")
cal.add("X-WR-CALNAME", "St Ann School Calendar")
cal.add("summary", "St Ann School Calendar")


tz = Timezone()
tz.add('tzid', 'America/Chicago')

standard = TimezoneStandard()
standard.add('dtstart', datetime(2025, 11, 2, 2, 0, 0))
standard.add('tzoffsetfrom', timedelta(hours=-5))
standard.add('tzoffsetto', timedelta(hours=-6))
standard.add('rrule', {'freq': 'yearly', 'bymonth': 11, 'byday': '1SU'})
standard.add('tzname', 'CST')
tz.add_component(standard)

daylight = TimezoneDaylight()
daylight.add('dtstart', datetime(2025, 3, 9, 2, 0, 0))
daylight.add('tzoffsetfrom', timedelta(hours=-6))
daylight.add('tzoffsetto', timedelta(hours=-5))
daylight.add('rrule', {'freq': 'yearly', 'bymonth': 3, 'byday': '2SU'})
daylight.add('tzname', 'CDT')
tz.add_component(daylight)

uid_i = 0
cal.add_component(tz)
for event_dict in event_data:
    print(event_dict["My Summary"])
    dt_start = datetime.strptime(event_dict['Start Date'], date_fmt)
    dt_end = datetime.strptime(event_dict['End Date'], date_fmt)

    if event_dict['All Day Event'] != 'TRUE':
        start_time = datetime.strptime(event_dict['Start Time'], time_fmt).time()
        end_time = datetime.strptime(event_dict['End Time'], time_fmt).time()

        dt_start = datetime.combine(dt_start.date(), start_time)
        dt_end = datetime.combine(dt_end.date(), end_time)      
    else:
        dt_end = dt_start + timedelta(days=1)

    dt_start = dt_start.replace(tzinfo=CT)
    dt_end = dt_end.replace(tzinfo=CT)

    summary = event_dict['My Summary']
    
    event = Event()
    event.add('uid', f"{uid_i}@school-calendar")
    event.add('summary', summary)
    event.add('categories', 'Kids')
    event.add('X-MICROSOFT-CDO-BUSYSTATUS', event_dict['X-MICROSOFT-CDO-BUSYSTATUS'])
    event.add('dtstart', dt_start)
    event.add('dtend',  dt_end)
    uid_i += 1

    alarm_1 = Alarm()
    alarm_1.add('action', 'DISPLAY')
    alarm_1.add("X-WR-ALARMUID", str(uuid.uuid4()).upper())
    if event_dict['Alarm Hours Before 1'] != '':
        hours_before = float(event_dict['Alarm Hours Before 1'])
        desc = hours_to_human_desc(summary, hours_before)

        alarm_1.add('trigger', timedelta(hours=-hours_before))
        alarm_1.add('description', desc)
    else:
        alarm_1.add('trigger', timedelta(hours=-(7*24)))
        alarm_1.add('description', f"7 days to {summary}")
    
    event.add_component(alarm_1)


    alarm_2 = Alarm()
    alarm_2.add('action', 'DISPLAY')
    alarm_2.add("X-WR-ALARMUID", str(uuid.uuid4()).upper())
    if event_dict['Alarm Hours Before 2'] != '':
        hours_before = float(event_dict['Alarm Hours Before 2'])
        desc = hours_to_human_desc(summary, hours_before)

        alarm_2.add('trigger', timedelta(hours=-hours_before))
        alarm_2.add('description', desc)
    else:
        alarm_2.add('trigger', timedelta(hours=-24))
        alarm_2.add('description', f"TOMORROW: {summary}")

    event.add_component(alarm_2)

    cal.add_component(event)

with open(cal_out_path, 'wb') as f:
    f.write(cal.to_ical())


# ics_path = Path("./St Ann School Calendar.ics")
# calendar = icalendar.Calendar.from_ical(ics_path.read_bytes())
# for event in calendar.events:
#     print(event.get("SUMMARY"))

