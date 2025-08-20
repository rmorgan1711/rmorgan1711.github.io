import icalendar
import csv
from pathlib import Path
from datetime import datetime, date, time

def vevent_props_to_str(v):
    """Convert vDDDType to a human-readable string."""

    if not isinstance(v, icalendar.prop.vDDDTypes):
        return str(v)
    
    dt = v.dt
    if isinstance(dt, datetime):
        v_str = dt.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(dt, date):
        v_str = dt.strftime('%Y-%m-%d')
    elif isinstance(dt, time):
        v_str = dt.strftime('%H:%M:%S')
    else:
        v_str = str(dt)
        
    return v_str
       

ics_path = Path("St Ann Official Calendar 2025-08-19.ics")
csv_path = Path("St Ann Official Calendar Export 2025-08-19.csv")

calendar = icalendar.Calendar.from_ical(ics_path.read_bytes())

# Collect all unique top-level VEVENT property names
property_names = set()
events = []
for component in calendar.walk():
    if component.name == "VEVENT":
        event_props = {}
        for k, v in component.items():
            event_props[k] = vevent_props_to_str(v)
            property_names.add(k)
        events.append(event_props)

property_names = sorted(property_names)

for e in events:
    if "Part Time Morning" in e["SUMMARY"]:
        test = e
        break

# Write to CSV
with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=property_names)
    writer.writeheader()
    for event in events:
        writer.writerow({k: event.get(k, "") for k in property_names})
