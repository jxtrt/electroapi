"""Module defining data point schemas."""

from datetime import datetime
from pydantic import BaseModel
from .area import GeoLimit


class PriceDataPoint(BaseModel):
    """
    Schema for a data point.
    """

    timestamp: datetime  # utc, ofc
    price: float
    unit: str = "€/MWh"
    geo_limit: GeoLimit


# other datapoints if needed
