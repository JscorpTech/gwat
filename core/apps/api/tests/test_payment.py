from core.apps.api.services.payment import calc_energy_price
from core.apps.shared.models import SettingsModel, OptionsModel


def test_calc_energy_price(db):
    OptionsModel.objects.create(key="price", settings=SettingsModel.objects.create(key="energy"), value=[1000])
    res = calc_energy_price(10)
    assert type(res) is float
    assert res == 10.0
