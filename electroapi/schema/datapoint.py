"""Module defining data point schemas."""

from datetime import datetime
from pydantic import BaseModel
from .area import Area


class PriceDataPoint(BaseModel):
    """
    Schema for a data point.
    """

    timestamp: datetime  # utc, ofc
    price: float
    area: Area


# other datapoints if needed
