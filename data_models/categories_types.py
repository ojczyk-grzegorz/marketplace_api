from enum import Enum


class VehiclesTypes(Enum):
    car = "car"
    motor = "motor"
    bicycle = "bicycle"
    cart = "cart"


class ElectronicsTypes(Enum):
    laptop = "laptop"
    tablet = "tablet"
    phone = "phone"


class ServicesTypes(Enum):
    cleaning = "cleaning"
    renovation = "renovation"
    other = "other"