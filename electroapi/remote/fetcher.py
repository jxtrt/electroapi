"""Module for fetching remote data."""

from datetime import datetime
import zoneinfo

import requests
import pandas as pd


class Fetcher:
    """Fetcher class for remote data."""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.cache = {}
        self.cache_date = None
        self.token = token

    def _call(self, endpoint: str, params: dict = None) -> dict:
        """Make a GET request to the remote API."""
        headers = {
            "Accept": "application/json; application/vnd.esios-api-v1+json",
            "Content-Type": "application/json",
            "Host": "api.esios.ree.es",
            "x-api-key": self.token,
        }

        response = requests.get(
            f"{self.base_url}/{endpoint}", headers=headers, params=params
        )
        response.raise_for_status()
        return response.json()

    def _today(self) -> list:
        """Fetch today's data from the remote API if not cached."""
        local_date = datetime.now(tz=zoneinfo.ZoneInfo("Europe/Madrid")).date()

        # check cache
        if self.cache_date and self.cache_date == local_date and "today" in self.cache:
            return self.cache["today"]

        # call
        response = self._call("indicators/1001")

        # store only the relevant part in cache
        self.cache["today"] = response["indicator"]["values"]
        self.cache_date = local_date

        return self.cache["today"]

    def _sanitize_geo_name(self, geo_name: str) -> str:
        """Sanitize the geo_limit value based on known valid values."""
        valid_limits = {"peninsular", "canarias", "baleares", "ceuta", "melilla"}
        geo_name_lower = geo_name.lower()
        if geo_name_lower in valid_limits:
            return geo_name_lower
        return "peninsular"

    def today(self) -> pd.DataFrame:
        """Get today's data as a DataFrame."""
        data = self._today()

        df = pd.DataFrame(data)

        df = df.rename(columns={"value": "price"})
        df["geo_limit"] = df["geo_name"].apply(self._sanitize_geo_name)
        df = df.drop(columns=["tz_time", "geo_id", "geo_name", "datetime_utc"])
        df["timestamp"] = pd.to_datetime(df["datetime"], errors="coerce")
        df["hour"] = df["timestamp"].dt.hour
        return df
