import pytest

from afg_province_maps.names import norm_name


@pytest.mark.parametrize("raw, key", [
    ("Kabul", "kabul"),
    ("Kabul Province", "kabul"),
    ("Hilmand", "helmand"),
    ("Sar-e Pol", "sar e pul"),
    ("Sar-e Pul", "sar e pul"),
    ("Bāmyān", "bamyan"),
    ("Dai Kundi", "daykundi"),
    ("Nimroz", "nimruz"),
    ("Ghanzi", "ghazni"),
    ("Maidan Wardak", "wardak"),
])
def test_norm_name(raw, key):
    assert norm_name(raw) == key
