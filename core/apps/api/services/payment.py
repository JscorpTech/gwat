from core.apps.shared.utils.settings import energy_price


def calc_energy_price(energy: int) -> float:
    """energiya narxini xisoblash

    Args:
        energy: [TODO:description]

    Returns:
        float
    """
    price = energy_price()
    return price * (energy / 1000)
