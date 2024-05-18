from uuid import uuid4

from data_models.categories import (
    Categories,
    ItemVehicle,
    ItemService,
    ItemElectronics
)
from data_models.categories_types import (
    VehiclesTypes,
    ElectronicsTypes,
    ServicesTypes
)


items_vehicles = [
    ItemVehicle(id=uuid4(), name="Skoda Fabia", types=[VehiclesTypes.car]),
    ItemVehicle(id=uuid4(), name="BMW x55", types=[VehiclesTypes.car]),
    ItemVehicle(id=uuid4(), name="Tesla 4", types=[VehiclesTypes.car])
]

items_electronics = [
    ItemElectronics(id=uuid4(), name="Lenovo ThinkPad U14 Gen. 3", types=[ElectronicsTypes.laptop]),
    ItemElectronics(id=uuid4(), name="Samsung S23", types=[ElectronicsTypes.phone]),
    ItemElectronics(id=uuid4(), name="iPad Air 5 64", types=[ElectronicsTypes.tablet])
]

items_services = [
    ItemService(id=uuid4(), name="Office cleaning Los Angeles", types=[ServicesTypes.cleaning]),
    ItemService(id=uuid4(), name="Apartment renovation New York", types=[ServicesTypes.renovation]),
    ItemService(id=uuid4(), name="Dog walking Denver", types=[ServicesTypes.other])
]

items = {
    Categories.vehicles: items_vehicles,
    Categories.electronics: items_electronics,
    Categories.services: items_services
}


def get_items(category: Categories | None = None) -> list:
    if isinstance(category, Categories):
        return items.get(category, [])
    return items