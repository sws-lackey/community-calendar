#!/usr/bin/env python3
"""
Scraper for Lyric Stage Company of Boston (lyricstage.com).

Step 1: Fetch /whats-on/ to discover productions (title, image, more-info URL,
        buy-tickets ID).
Step 2: For each production, fetch /buy-tickets/?id=N to get individual
        performance dates/times from server-rendered HTML.

Usage:
    python scrapers/lyric_stage.py -o cities/boston/lyric_stage.ics
"""

import re
import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])

from datetime import datetime, timedelta
from typing import Any

import requests
from bs4 import BeautifulSoup
from scrapers.lib.base import BaseScraper
from scrapers.lib.utils import DEFAULT_HEADERS

BASE_URL = "https://www.lyricstage.com"


class LyricStageScraper(BaseScraper):
    name = "Lyric Stage Company"
    domain = "lyricstage.com"
    timezone = "America/New_York"

    def fetch_events(self) -> list[dict[str, Any]]:
        productions = self._fetch_productions()
        self.logger.info(f"Found {len(productions)} productions")

        events = []
        for prod in productions:
            showtimes = self._fetch_showtimes(prod)
            events.extend(showtimes)
            self.logger.info(f"  {prod['title']}: {len(showtimes)} performances")

        return events

    def _fetch_productions(self) -> list[dict]:
        """Scrape /whats-on/ for production cards."""
        resp = requests.get(f"{BASE_URL}/whats-on/", headers=DEFAULT_HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        productions = []
        for link in soup.find_all('a', href=lambda h: h and 'buy-tickets' in h):
            buy_href = link['href']
            match = re.search(r'[?&]id=(\d+)', buy_href)
            if not match:
                continue
            ticket_id = match.group(1)

            # Walk up to find the card container with image and title
            card = link
            for _ in range(8):
                if card.parent:
                    card = card.parent
                imgs = card.find_all('img')
                h_tags = card.find_all(['h2', 'h3', 'h4'])
                if imgs and h_tags:
                    break

            title = h_tags[0].get_text(strip=True) if h_tags else ''
            if not title:
                continue

            # Image
            image_url = ''
            if imgs:
                image_url = imgs[0].get('src', '')

            # More info link (production page)
            info_url = ''
            for a in card.find_all('a', href=True):
                if '/production/' in a['href']:
                    info_url = a['href']
                    if not info_url.startswith('http'):
                        info_url = BASE_URL + info_url
                    break

            productions.append({
                'title': title,
                'ticket_id': ticket_id,
                'image_url': image_url,
                'info_url': info_url,
            })

        return productions

    def _fetch_showtimes(self, prod: dict) -> list[dict]:
        """Scrape /buy-tickets/?id=N for performance dates/times."""
        url = f"{BASE_URL}/buy-tickets/?id={prod['ticket_id']}"
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        events = []
        for h3 in soup.find_all('h3'):
            date_text = h3.get_text(strip=True)
            # Match "Friday, March 20, 2026"
            date_match = re.match(
                r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+'
                r'(\w+ \d{1,2}, \d{4})', date_text)
            if not date_match:
                continue

            try:
                base_date = datetime.strptime(date_match.group(1), '%B %d, %Y')
            except ValueError:
                continue

            # Find time entries in sibling div
            card = h3.parent
            for p in card.find_all('p'):
                time_text = p.get_text(strip=True)
                time_match = re.match(r'(\d{1,2}:\d{2}[ap]m)', time_text, re.IGNORECASE)
                if not time_match:
                    continue

                dt = self._parse_time(base_date, time_match.group(1))
                if not dt:
                    continue

                events.append({
                    'title': prod['title'],
                    'dtstart': dt,
                    'dtend': dt + timedelta(hours=2, minutes=30),
                    'url': prod['info_url'],
                    'location': 'Lyric Stage Company, 140 Clarendon St, Boston, MA',
                    'image_url': prod.get('image_url', ''),
                })

        return events

    def _parse_time(self, date, time_str):
        """Combine date with time like '7:30pm'."""
        time_str = time_str.strip().upper()
        m = re.match(r'(\d{1,2}):(\d{2})\s*(AM|PM)', time_str)
        if not m:
            return None
        hour, minute, ampm = int(m.group(1)), int(m.group(2)), m.group(3)
        if ampm == 'PM' and hour != 12:
            hour += 12
        elif ampm == 'AM' and hour == 12:
            hour = 0
        return date.replace(hour=hour, minute=minute)

    @classmethod
    def main(cls):
        cls.setup_logging()
        args = cls.parse_args(description='Scrape Lyric Stage Company performances')
        if args.debug:
            import logging
            logging.getLogger().setLevel(logging.DEBUG)
        scraper = cls()
        scraper.run(output=args.output)


if __name__ == '__main__':
    LyricStageScraper.main()
