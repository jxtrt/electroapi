"""Main entry point for the ElectroAPI application."""

import json
import os
from typing import List

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI

from electroapi.schema import Area, PriceDataPoint, GeoLimit
from electroapi.remote.fetcher import Fetcher

load_dotenv()
app = FastAPI()

base_url = os.getenv("BASE_ESIOS_API_URL", "https://api.esios.ree.es")
fetcher = Fetcher(base_url=base_url)  # init here to preserve obj state (cache)


@app.get("/areas", response_model=List[Area])
async def get_areas():
    """
    Get the list of areas from a local JSON file.
    Return an array of Area objects.
    """
    # parsing json directly here is just cleaner
    areas_json_path = os.getenv("AREAS_JSON_PATH", "./data/areas.json")

    try:
        with open(areas_json_path, "r", encoding="utf-8") as f:
            areas_data = json.load(f)["areas"]
            return [Area(**area) for area in areas_data]
    except FileNotFoundError:
        return {"error": "Areas file not found."}
    except (json.JSONDecodeError, ValueError):
        return {"error": "Error decoding areas JSON file."}


@app.get("/today")
async def get_today(geo_limit: GeoLimit = GeoLimit.PENINSULAR):
    """
    Get today's data from the remote API.
    """

    try:

        def _sanitize_geo_name(geo_name: str) -> str:
            """Sanitize the geo_limit value based on known valid values."""
            valid_limits = {"peninsular", "canarias", "baleares", "ceuta", "melilla"}
            geo_name_lower = geo_name.lower()
            if geo_name_lower in valid_limits:
                return geo_name_lower
            return "peninsular"

        data = fetcher.today()
        df = pd.DataFrame(data)

        df = df.rename(columns={"value": "price"})
        df["geo_limit"] = df["geo_name"].apply(_sanitize_geo_name)
        df = df.drop(columns=["datetime", "tz_time", "geo_id", "geo_name"])
        df["timestamp"] = pd.to_datetime(df["datetime_utc"], errors="coerce")
        df = df.drop(columns=["datetime_utc"])

        # simple filtering by geo_limit
        df = df[df["geo_limit"] == geo_limit.value]

        # construct response as array of PriceDataPoint
        response = [PriceDataPoint(**row) for row in df.to_dict(orient="records")]

        return response
    except Exception as e:
        return {"error": str(e)}
