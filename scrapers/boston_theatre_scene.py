#!/usr/bin/env python3
"""
Scraper for Boston Theatre Scene calendar (bostontheatrescene.com).

This is an aggregator of Boston-area theater events. The calendar page
loads events via a WordPress AJAX endpoint (action=calendar) which returns
JSON with HTML fragments for each event instance.

Usage:
    python scrapers/boston_theatre_scene.py -o cities/boston/boston_theatre_scene.ics
"""

import json
import logging
import re
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from zoneinfo import ZoneInfo

import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])
from scrapers.lib.base import BaseScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

AJAX_URL = 'https://www.bostontheatrescene.com/admin/wp-admin/admin-ajax.php'
TZ = ZoneInfo('America/New_York')


class BostonTheatreSceneScraper(BaseScraper):
    name = 'Boston Theatre Scene'
    domain = 'bostontheatrescene.com'
    timezone = 'America/New_York'

    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://www.bostontheatrescene.com/calendar/',
        })

    def fetch_events(self):
        """Fetch all events from the AJAX calendar endpoint."""
        # The endpoint expects serializeArray() format for filters
        data = {
            'action': 'calendar',
            'filters[0][name]': 'date',
            'filters[0][value]': '',
            'filters[1][name]': 'event',
            'filters[1][value]': '',
            'filters[2][name]': 'presenter',
            'filters[2][value]': '',
        }

        try:
            resp = self.session.post(AJAX_URL, data=data, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            logger.error(f'Failed to fetch calendar: {e}')
            return []

        try:
            result = resp.json()
        except json.JSONDecodeError as e:
            logger.error(f'Failed to parse JSON: {e}')
            return []

        instances = result.get('instances', {})
        count = result.get('instanceCount', 0)
        logger.info(f'Received {count} instances across {len(instances)} dates')

        events = []
        seen = set()
        for date_str, items in instances.items():
            base_date = self._parse_date_header(date_str)
            if not base_date:
                continue

            for html in items:
                event = self._parse_event(html, base_date)
                if event:
                    key = f'{event["title"]}|{event["dtstart"].isoformat()}'
                    if key not in seen:
                        seen.add(key)
                        events.append(event)

        logger.info(f'Parsed {len(events)} events')
        return events

    def _parse_date_header(self, date_str):
        """Parse 'Thursday March 12, 2026' into a date."""
        # Strip day-of-week prefix
        date_str = re.sub(r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+',
                          '', date_str)
        try:
            return datetime.strptime(date_str, '%B %d, %Y')
        except ValueError:
            logger.warning(f'Could not parse date: {date_str}')
            return None

    def _parse_event(self, html, base_date):
        """Parse an event HTML fragment into an event dict."""
        soup = BeautifulSoup(html, 'html.parser')

        # Title contains time: "7:00pm— We Had a World"
        title_el = soup.find(class_='c-calendar-instance__title')
        if not title_el:
            return None

        raw_title = title_el.get_text(strip=True)

        # Extract time and clean title
        time_match = re.match(r'(\d{1,2}:\d{2}[ap]m)\s*[—–-]\s*(.*)', raw_title, re.IGNORECASE)
        if time_match:
            time_str = time_match.group(1)
            title = time_match.group(2).strip()
            dt = self._combine_date_time(base_date, time_str)
        else:
            title = raw_title
            dt = base_date.replace(hour=19, minute=30, tzinfo=TZ)

        if not title or not dt:
            return None

        # Venue
        venue_el = soup.find(class_='c-calendar-instance__venue')
        venue = venue_el.get_text(strip=True) if venue_el else ''

        # URL
        link = soup.find('a', class_='c-calendar-instance__event-link')
        url = link['href'] if link else ''

        # Image
        img = soup.find('img')
        image_url = ''
        if img:
            srcset = img.get('data-srcset', '')
            # Get the largest image from srcset
            for part in srcset.split(','):
                part = part.strip()
                if '450w' in part or '300w' in part:
                    image_url = part.split(' ')[0]
                    break
            if not image_url and srcset:
                image_url = srcset.split(',')[0].strip().split(' ')[0]

        return {
            'title': title,
            'dtstart': dt,
            'dtend': dt + timedelta(hours=2),
            'url': url,
            'location': venue,
            'image_url': image_url,
        }

    def _combine_date_time(self, date, time_str):
        """Combine a date with a time string like '7:00pm'."""
        time_str = time_str.strip().upper()
        m = re.match(r'(\d{1,2}):(\d{2})\s*(AM|PM)', time_str)
        if not m:
            return None
        hour, minute, ampm = int(m.group(1)), int(m.group(2)), m.group(3)
        if ampm == 'PM' and hour != 12:
            hour += 12
        elif ampm == 'AM' and hour == 12:
            hour = 0
        return date.replace(hour=hour, minute=minute, tzinfo=TZ)

    @classmethod
    def main(cls):
        cls.setup_logging()
        args = cls.parse_args(description='Scrape Boston Theatre Scene calendar')
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
        scraper = cls()
        scraper.run(output=args.output)


if __name__ == '__main__':
    BostonTheatreSceneScraper.main()
