#!/usr/bin/env python3
"""Scraper for Evanston events via CitySpark API."""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])  # Add scrapers/ to path

from lib.cityspark import EvanstonCitySparkScraper

if __name__ == '__main__':
    EvanstonCitySparkScraper.main()
