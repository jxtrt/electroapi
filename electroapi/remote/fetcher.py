"""Module for fetching remote data."""

from datetime import datetime
import zoneinfo
import requests


class Fetcher:
    """Fetcher class for remote data."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.cache = {}
        self.cache_date = None

    def today(self):
        """Fetch today's data from the remote API if not cached."""
        local_date = datetime.now(tz=zoneinfo.ZoneInfo("Europe/Madrid")).date()

        # check cache
        if self.cache_date and self.cache_date == local_date and "today" in self.cache:
            return self.cache["today"]

        # call
        response = requests.get(f"{self.base_url}/indicators/1001")
        response.raise_for_status()

        # store only the relevant part in cache
        self.cache["today"] = response.json()["indicator"]["values"]
        self.cache_date = local_date

        return self.cache["today"]
