"""Main entry point for the ElectroAPI application."""

import json
import os
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI

from electroapi.schema import Area

load_dotenv()
app = FastAPI()


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
            areas_data = json.load(f)
            return [Area(**area) for area in areas_data]
    except FileNotFoundError:
        return {"error": "Areas file not found."}
    except (json.JSONDecodeError, ValueError):
        return {"error": "Error decoding areas JSON file."}
