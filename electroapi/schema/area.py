"""Schema definitions for geographical areas."""

from enum import Enum
from pydantic import BaseModel


class GeoLimit(str, Enum):
    """Geographical limits for areas."""

    CCAA = "ccaa"
    PENINSULAR = "peninsular"
    CANARIAS = "canarias"
    BALEARES = "baleares"
    CEUTA = "ceuta"
    MELILLA = "melilla"


class Area(BaseModel):
    """
    Schema for an area.
    Harvested from hardcoded values on https://www.ree.es/themes/custom/ree/js/ree.js?t1jmnh
    """

    geo_name: str
    geo_limit: GeoLimit
    geo_id: int
