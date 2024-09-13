from ics import Calendar
from datetime import datetime, timedelta
import pytz
import arrow
from pathlib import Path
import re
from typing import List, Dict, Union
from dotenv import dotenv_values
config = dotenv_values(".env")
paris_tz = pytz.timezone('Europe/Paris')

menus = [config['MENU1'], config['MENU2'], config['MENU3'], config['MENU4']]
def clean_description(description):
    pattern = r"\(Exporté le:\s*\d{2}/\d{2}/\d{4}\s*\d{2}:\d{2}\)"
    cleaned_description = re.sub(pattern, "", description).strip()
    return cleaned_description

def open_ics(file_path: str) -> bytes:
    return Path(file_path).read_bytes()

def parse_ics(ics_content: bytes):
    calendar = Calendar(ics_content.decode('utf-8'))
    return list(calendar.events)

def format_date(dt: datetime) -> str:
    return dt.strftime('%d/%m/%Y')

def format_time(dt: datetime) -> str:
    return dt.strftime('%H:%M')

def get_events_for_today(menu: int):
    ics_content = open_ics(f'menu{menu + 1}.ics')
    events = parse_ics(ics_content)
    today = datetime.now(pytz.utc).date()

    return [
        {
            'name': event.name,
            'begin': event.begin,
            'date': arrow.get(event.begin).to(paris_tz).format('DD/MM/YYYY'),
            'heure': arrow.get(event.begin).to(paris_tz).format('HH:mm'),
            'end': arrow.get(event.end).to(paris_tz).format('HH:mm'),
            'description': clean_description(event.description),
            'location': event.location or 'Non spécifiée'
        }
        for event in events if event.begin.date() == today
    ]

def get_events_for_tomorrow(menu: int):
    ics_content = open_ics(f'menu{menu + 1}.ics')
    events = parse_ics(ics_content)
    tomorrow = (datetime.now(pytz.utc) + timedelta(days=1)).date()

    return [
        {
            'name': event.name,
            'begin': event.begin,
            'date': arrow.get(event.begin).to(paris_tz).format('DD/MM/YYYY'),
            'heure': arrow.get(event.begin).to(paris_tz).format('HH:mm'),
            'end': arrow.get(event.end).to(paris_tz).format('HH:mm'),
            'description': clean_description(event.description),
            'location': event.location or 'Non spécifiée'
        }
        for event in events if event.begin.date() == tomorrow
    ]

def get_next_event(menu: int):
    ics_content = open_ics(f'menu{menu + 1}.ics')
    events = parse_ics(ics_content)
    now = datetime.now(pytz.utc)
    upcoming_events = [event for event in events if event.begin > now]

    if not upcoming_events:
        return None

    next_event = min(upcoming_events, key=lambda e: e.begin)

    return {
        'name': next_event.name,
        'begin': next_event.begin,
        'date': format_date(next_event.begin),
        'heure': arrow.get(next_event.begin).to(paris_tz).format('HH:mm'),
        'end': arrow.get(next_event.end).to(paris_tz).format('HH:mm'),
        'description': clean_description(next_event.description),
        'location': next_event.location or 'Non spécifiée'
    }


def get_events_for_next_30_days(menu: int) -> List[Dict[str, Union[str, List[Dict[str, str]]]]]:
    ics_content = open_ics(f'menu{menu + 1}.ics')
    events = parse_ics(ics_content)

    today = datetime.now(pytz.utc).date()
    end_date = today + timedelta(days=30)

    days_events = {}
    current_date = today
    while current_date <= end_date:
        day_name = current_date.strftime('%A')
        days_events[current_date] = {
            'day_name': day_name,
            'date': format_date(current_date),
            'events': []
        }
        current_date += timedelta(days=1)

    for event in events:
        event_date = event.begin.date()
        if today <= event_date <= end_date:
            day_name = event_date.strftime('%A')
            days_events[event_date]['events'].append({
                'name': event.name,
                'begin': event.begin,
                'date': arrow.get(event.begin).to(paris_tz).format('DD/MM/YYYY'),
                'heure': arrow.get(event.begin).to(paris_tz).format('HH:mm'),
                'end': arrow.get(event.end).to(paris_tz).format('HH:mm'),
                'description': clean_description(event.description),
                'location': event.location or 'Non spécifiée'
            })

    for date, day_info in days_events.items():
        if not day_info['events']:
            day_info['events'] = [{'name': 'Aucun cours', 'description': 'Aucun événement prévu pour ce jour'}]

    return list(days_events.values())
