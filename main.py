"""Main entry point for the ElectroAPI application."""

import json
import os
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
import uvicorn

from electroapi.scheduler import Scheduler
from electroapi.schema import Area, PriceDataPoint, GeoLimit
from electroapi.remote.fetcher import Fetcher
from electroapi.api.rate_limit import RateLimitMiddleware

load_dotenv()

MAX_REQUESTS = 10
WINDOW_SECONDS = 60

app = FastAPI()


fetcher = Fetcher(
    base_url=os.getenv("BASE_ESIOS_API_URL", "https://api.esios.ree.es"),
    token=os.getenv("ESIOS_API_TOKEN"),
)  # inits here to preserve obj state (cache)

app.add_middleware(
    RateLimitMiddleware, max_requests=MAX_REQUESTS, window_seconds=WINDOW_SECONDS
)


@app.get("/areas", response_model=List[Area])
async def get_areas():
    """
    Get the list of areas from a local JSON file.
    Return an array of Area objects.
    """
    # parsing json directly here is just cleaner
    areas_json_path = os.getenv("AREAS_JSON_PATH", "./electroapi/data/areas.json")

    try:
        with open(areas_json_path, "r", encoding="utf-8") as f:
            areas_data = json.load(f)["areas"]
            return [Area(**area) for area in areas_data]
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Areas file not found.")
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(status_code=500, detail="Error retrieving areas data.")


@app.get("/today")
async def get_today(geo_limit: GeoLimit = GeoLimit.PENINSULAR):
    """
    Get today's data from the remote API.
    """

    try:
        data = fetcher.today()

        # simple filtering by geo_limit
        data = data[data["geo_limit"] == geo_limit.value]

        # construct response as array of PriceDataPoint
        response = [PriceDataPoint(**row) for row in data.to_dict(orient="records")]

        return response
    except Exception:
        raise HTTPException(status_code=500)


@app.get("/schedule")
async def get_scheduling(
    power_on_hours: int,
    max_blocks: int = None,
    geo_limit: GeoLimit = GeoLimit.PENINSULAR,
):
    """
    Get today's data from the remote API.
    Given a number of power-on hours needed, return the optimal schedule.
    """

    if power_on_hours > 24:
        raise HTTPException(
            status_code=400, detail="power_on_hours must be less than or equal to 24."
        )
    if geo_limit == GeoLimit.CCAA:
        raise HTTPException(
            status_code=400, detail="geo_limit cannot be 'ccaa' for scheduling."
        )

    try:

        data = fetcher.today()
        data = data[data["geo_limit"] == geo_limit.value]
        scheduler = Scheduler(data)
        schedule = scheduler.schedule(
            power_on_hours=power_on_hours, max_blocks=max_blocks
        )

        if schedule.empty:
            raise HTTPException(
                status_code=422,
                detail="No valid schedule found with the given parameters.",
            )

        ret_schedule = [
            PriceDataPoint(**row) for row in schedule.to_dict(orient="records")
        ]
        cost_sum = sum(ret_schedule[i].price for i in range(len(ret_schedule)))
        total_blocks = scheduler.n_blocks(
            [(row.timestamp.hour,) for row in ret_schedule]
        )

        return {
            "schedule": ret_schedule,
            "cost_sum": cost_sum,
            "total_blocks": total_blocks,
        }

    except Exception:
        raise HTTPException(status_code=500)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
