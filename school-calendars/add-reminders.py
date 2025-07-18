import icalendar
from icalendar import Calendar, Event, Alarm, Timezone, TimezoneStandard, TimezoneDaylight
from datetime import timedelta, datetime
from pathlib import Path
import csv
import zoneinfo

cal_out_path = Path("./St Ann School Calendar.ics")

data_path = Path("./St Ann School Calendar.csv")
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

cal.add_component(tz)

event_dict = event_data[1]
for event_dict in event_data:
    dt_start = datetime.strptime(event_dict['Start Date'], date_fmt)
    dt_end = datetime.strptime(event_dict['End Date'], date_fmt)

    if event_dict['All Day Event'] != 'TRUE':
        start_time = datetime.strptime(event_dict['Start Time'], time_fmt).time()
        end_time = datetime.strptime(event_dict['End Time'], time_fmt).time()

        dt_start = datetime.combine(dt_start.date(), start_time)
        dt_end = datetime.combine(dt_end.date(), end_time)      
    else:
        dt_end = dt_end + timedelta(days=1)

    dt_start = dt_start.replace(tzinfo=CT)
    dt_end = dt_end.replace(tzinfo=CT)

    event = Event()
    event.add('summary', event_dict['Subject'])
    event.add('categories', 'Kids')
    event.add('X-MICROSOFT-CDO-BUSYSTATUS', 'OOF')
    event.add('dtstart', dt_start)
    event.add('dtend',  dt_end)

    alarm_1 = Alarm()
    alarm_1.add('action', 'DISPLAY')
    alarm_1.add('trigger', timedelta(hours=-(7*24)))
    alarm_1.add('description', f"7 days to {event_dict['Subject']}")
    event.add_component(alarm_1)

    alarm_2 = Alarm()
    alarm_2.add('action', 'DISPLAY')
    alarm_2.add('trigger', timedelta(hours=-24))
    alarm_2.add('description', f"TOMORROW: {event_dict['Subject']}")
    event.add_component(alarm_1)

    cal.add_component(event)

with open(cal_out_path, 'wb') as f:
    f.write(cal.to_ical())


ics_path = Path("./St Ann School Calendar.ics")
calendar = icalendar.Calendar.from_ical(ics_path.read_bytes())
for event in calendar.events:
    print(event.get("SUMMARY"))

