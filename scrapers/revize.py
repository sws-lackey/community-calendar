#!/usr/bin/env python3
"""
Scraper for Revize CMS calendar events.

Revize sites expose a JSON calendar feed at:
  /_assets_/plugins/revizeCalendar/calendar_data_handler.php

Usage:
    python scrapers/revize.py \
        --webspace evanstonil --host cityofevanston.org \
        --name "City of Evanston" --categories "Events" \
        --output cities/evanston/city_of_evanston.ics
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import argparse
import json
import logging
from datetime import datetime
from typing import Any
from urllib.parse import unquote
from urllib.request import urlopen, Request

from lib.base import BaseScraper

logger = logging.getLogger(__name__)

DATA_HANDLER = "/_assets_/plugins/revizeCalendar/calendar_data_handler.php"


class RevizeScraper(BaseScraper):
    name = "Revize Calendar"
    domain = "revize.com"
    timezone = "America/Chicago"

    def __init__(self, host: str, webspace: str, categories: list[str] | None = None,
                 source_name: str | None = None):
        super().__init__()
        self.host = host
        self.webspace = webspace
        self.categories = [c.lower() for c in categories] if categories else None
        if source_name:
            self.name = source_name
        self.domain = host

    def _fetch_json(self) -> list[dict]:
        url = (f"https://{self.host}{DATA_HANDLER}"
               f"?webspace={self.webspace}"
               f"&relative_revize_url=//cms6.revize.com"
               f"&protocol=https:")
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))

    def fetch_events(self) -> list[dict[str, Any]]:
        data = self._fetch_json()
        logger.info("Fetched %d total events from %s", len(data), self.host)

        events = []
        for item in data:
            if self.categories:
                cal_name = (item.get('primary_calendar_name') or '').lower()
                if cal_name not in self.categories:
                    continue

            event = self._parse_event(item)
            if event:
                events.append(event)

        logger.info("Found %d events after category filter", len(events))
        return events

    def _parse_event(self, item: dict) -> dict[str, Any] | None:
        title = item.get('title', '').strip()
        if not title:
            return None

        start_str = item.get('start')
        if not start_str:
            return None

        try:
            dtstart = datetime.fromisoformat(start_str)
        except ValueError:
            return None

        event = {
            'title': title,
            'dtstart': dtstart,
        }

        end_str = item.get('end')
        if end_str:
            try:
                event['dtend'] = datetime.fromisoformat(end_str)
            except ValueError:
                pass

        if item.get('location'):
            event['location'] = item['location']

        if item.get('url'):
            event['url'] = item['url']

        desc = item.get('desc', '')
        if desc:
            event['description'] = unquote(desc)

        return event


if __name__ == "__main__":
    RevizeScraper.setup_logging()
    parser = argparse.ArgumentParser(description="Scrape events from a Revize CMS calendar")
    parser.add_argument("--host", required=True, help="Site hostname (e.g. cityofevanston.org)")
    parser.add_argument("--webspace", required=True, help="Revize webspace ID (e.g. evanstonil)")
    parser.add_argument("--name", type=str, default="Revize Calendar", help="Source name")
    parser.add_argument("--categories", type=str, help="Comma-separated category names to include")
    parser.add_argument("--output", "-o", type=str, help="Output filename")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    categories = [c.strip() for c in args.categories.split(',')] if args.categories else None
    scraper = RevizeScraper(
        host=args.host,
        webspace=args.webspace,
        categories=categories,
        source_name=args.name,
    )
    scraper.run(output=args.output)
