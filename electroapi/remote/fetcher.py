"""Module for fetching remote data."""

import requests


class Fetcher:
    """Fetcher class for remote data."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.cache = {}

    def today(self):
        """Fetch today's data from the remote API."""
        response = requests.get(f"{self.base_url}/indicators/1001")
        response.raise_for_status()
        return response.json()["indicator"]["values"]
