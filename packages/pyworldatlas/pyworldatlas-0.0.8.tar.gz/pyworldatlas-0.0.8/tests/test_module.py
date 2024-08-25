import pytest
from pyworldatlas.atlas import Atlas


def test_get_capital():
    atlas = Atlas()
    algeria_profile = atlas.get_country_profile("Algeria")
    print(algeria_profile)
    assert algeria_profile["capital"]["name"] == "Algiers"


if __name__ == "__main__":
    pytest.main()
