from core.apps.shared.utils.settings import energy_price
import math


def calc_energy_price(energy: int) -> float:
    price = energy_price()
    return price * (energy / 1000)
