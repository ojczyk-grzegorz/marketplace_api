from pydantic import BaseModel, UUID4
from enum import Enum
from uuid import uuid4

from data_models.categories_types import (
    VehiclesTypes,
    ElectronicsTypes,
    ServicesTypes
)


class Categories(Enum):
    vehicles = "vehicles"
    estates = "estates"
    services = "services"
    clothes = "clothes"
    farming = "farming"
    activities = "activities"
    electronics = "electronics"



class Post(BaseModel):
    id: str | UUID4
    content: str


class Item(BaseModel):
    id: str | UUID4
    name: str
    description: str | None = None
    post_id: Post | None = None


class ItemVehicle(Item):
    category: Categories = Categories.vehicles
    types: list[VehiclesTypes]


class ItemElectronics(Item):
    category: Categories = Categories.electronics
    types: list[ElectronicsTypes]


class ItemService(Item):
    category: Categories = Categories.vehicles
    types: list[ServicesTypes]