from conftest import vcr_c  # noqa

from whitebit_httpx_client import WhiteBITClient


@vcr_c.use_cassette("assets/test_get_assets.yaml")
def test_get_assets(white_bit_client: WhiteBITClient):
    assets = white_bit_client.get_assets_data()
    assert isinstance(assets, dict)
    assert len(assets) > 100


@vcr_c.use_cassette("assets/test_get_assets.yaml")
async def test_async_get_assets(white_bit_client: WhiteBITClient):
    assets = await white_bit_client.async_get_assets_data()
    assert isinstance(assets, dict)
    assert len(assets) > 100
