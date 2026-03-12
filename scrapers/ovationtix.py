#!/usr/bin/env python3
"""
Scraper for OvationTix (AudienceView Professional) venues.

OvationTix hosts ticketing for many small/mid-size theaters. The ci.ovationtix.com
frontend is a React SPA behind Cloudflare, but web.ovationtix.com serves
server-rendered HTML:
  - /trs/cal/{orgId}         — lists all current productions
  - /trs/cal/{orgId}?productionId={id} — shows individual performance dates/times

Usage:
    python scrapers/ovationtix.py --org 2462 --name "Central Square Theater" -o cities/boston/central_square.ics
"""

import argparse
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

BASE_URL = 'https://web.ovationtix.com/trs/cal'


class OvationTixScraper(BaseScraper):
    name = 'OvationTix Venue'
    domain = 'ovationtix.com'
    timezone = 'America/New_York'

    def __init__(self, org_id, tz='America/New_York'):
        super().__init__()
        self.org_id = org_id
        self.tz = ZoneInfo(tz)
        self.timezone = tz
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; CommunityCalendar/1.0)'
        })

    def fetch_events(self):
        """Fetch all productions and their individual performances."""
        productions = self._fetch_productions()
        logger.info(f'Found {len(productions)} productions')

        events = []
        for prod in productions:
            perfs = self._fetch_performances(prod)
            events.extend(perfs)

        logger.info(f'Found {len(events)} total performances')
        return events

    def _fetch_productions(self):
        """Fetch the production listing page and extract production IDs/titles."""
        url = f'{BASE_URL}/{self.org_id}'
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            logger.error(f'Failed to fetch productions: {e}')
            return []

        soup = BeautifulSoup(resp.text, 'html.parser')
        productions = []

        # Productions are linked as ci.ovationtix.com/{orgId}/production/{prodId}
        for link in soup.find_all('a', href=re.compile(r'/production/(\d+)')):
            m = re.search(r'/production/(\d+)', link['href'])
            if not m:
                continue
            prod_id = m.group(1)
            text = link.get_text(strip=True)

            # Skip generic links like "buy now"
            if text.lower() in ('buy now »', 'buy now', ''):
                continue

            # Check if we already have this production
            if any(p['id'] == prod_id for p in productions):
                continue

            productions.append({'id': prod_id, 'title': text})

        # Merge multi-part titles (author + title + director are separate links)
        merged = {}
        for link in soup.find_all('a', href=re.compile(r'/production/(\d+)')):
            m = re.search(r'/production/(\d+)', link['href'])
            if not m:
                continue
            prod_id = m.group(1)
            text = link.get_text(strip=True)
            if text.lower() in ('buy now »', 'buy now', ''):
                continue
            merged.setdefault(prod_id, []).append(text)

        # Build final production list
        # Link pattern: author ("Hugh Whitemore's"), title ("Breaking the Code"),
        # director ("directed by Scott Edmiston"). Pick the title by excluding
        # author/director patterns.
        final = []
        seen = set()
        for prod_id, texts in merged.items():
            if prod_id in seen:
                continue
            seen.add(prod_id)
            # Filter out author credits (ending with 's) and director credits
            candidates = [t for t in texts
                          if not t.lower().startswith('directed by')
                          and not re.match(r".+('s|'s)$", t)]
            title = candidates[0] if candidates else texts[0]
            final.append({'id': prod_id, 'title': title})

        return final

    def _fetch_performances(self, production):
        """Fetch individual performance dates/times for a production."""
        url = f'{BASE_URL}/{self.org_id}?productionId={production["id"]}'
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            logger.warning(f'Failed to fetch performances for {production["title"]}: {e}')
            return []

        soup = BeautifulSoup(resp.text, 'html.parser')
        events = []

        # Performance times are links like /trs/pe.c/{performanceId} with time text
        # They appear grouped under date text
        # Strategy: find all text containing full dates and times
        text = soup.get_text()

        # Find date + time patterns in the page text
        # Dates appear as "Thursday, April 2, 2026" or similar
        current_date = None
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Try to match a full date like "Thursday, April 2, 2026"
            date_match = re.match(
                r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+'
                r'(\w+ \d{1,2},\s*\d{4})', line
            )
            if date_match:
                try:
                    current_date = datetime.strptime(date_match.group(1), '%B %d, %Y')
                except ValueError:
                    pass
                continue

            # Match time patterns like "7:30 PM" or "2:00 PM"
            if current_date:
                times = re.findall(r'(\d{1,2}:\d{2}\s*[AP]M)', line, re.IGNORECASE)
                for time_str in times:
                    dt = self._combine_date_time(current_date, time_str)
                    if dt:
                        events.append({
                            'title': production['title'],
                            'dtstart': dt,
                            'dtend': dt + timedelta(hours=2),
                            'url': f'https://ci.ovationtix.com/{self.org_id}/production/{production["id"]}',
                            'location': self._venue_name(soup),
                        })

        # Fallback: if no individual performances found, create one event per production
        if not events:
            logger.warning(f'No individual performances found for {production["title"]}, using date range')
            # Try to find date range from the listing
            range_match = re.search(
                r'(\w{3},\s+\w+ \d{1,2})\s*-\s*(\w{3},\s+\w+ \d{1,2})',
                text
            )
            if range_match:
                year = datetime.now().year
                try:
                    start = datetime.strptime(f'{range_match.group(1)}, {year}', '%a, %b %d, %Y')
                    events.append({
                        'title': production['title'],
                        'dtstart': start.replace(hour=19, minute=30, tzinfo=self.tz),
                        'dtend': start.replace(hour=21, minute=30, tzinfo=self.tz),
                        'url': f'https://ci.ovationtix.com/{self.org_id}/production/{production["id"]}',
                        'location': self._venue_name(soup),
                    })
                except ValueError:
                    pass

        return events

    def _combine_date_time(self, date, time_str):
        """Combine a date object with a time string like '7:30 PM'."""
        time_str = time_str.strip().upper()
        m = re.match(r'(\d{1,2}):(\d{2})\s*(AM|PM)', time_str)
        if not m:
            return None
        hour, minute, ampm = int(m.group(1)), int(m.group(2)), m.group(3)
        if ampm == 'PM' and hour != 12:
            hour += 12
        elif ampm == 'AM' and hour == 12:
            hour = 0
        return date.replace(hour=hour, minute=minute, tzinfo=self.tz)

    def _venue_name(self, soup):
        """Extract venue name from the page, or return default."""
        # Look for venue in table cells
        for td in soup.find_all('td'):
            text = td.get_text(strip=True)
            if 'theater' in text.lower() or 'theatre' in text.lower():
                if len(text) < 100:
                    return text
        return self.name

    @classmethod
    def parse_args(cls, description=None):
        parser = argparse.ArgumentParser(description=description or 'Scrape OvationTix venue')
        parser.add_argument('--org', required=True, help='OvationTix organization ID')
        parser.add_argument('--output', '-o', type=str, help='Output filename')
        parser.add_argument('--name', type=str, help='Source name override')
        parser.add_argument('--timezone', type=str, default='America/New_York', help='Timezone')
        parser.add_argument('--debug', action='store_true', help='Enable debug logging')
        return parser.parse_args()

    @classmethod
    def main(cls):
        cls.setup_logging()
        args = cls.parse_args()
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
        scraper = cls(org_id=args.org, tz=args.timezone)
        if args.name:
            scraper.name = args.name
        scraper.run(output=args.output)


if __name__ == '__main__':
    OvationTixScraper.main()
