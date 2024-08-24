from conftest import vcr_c  # noqa

from whitebit_httpx_client import WhiteBITClient  # noqa


# @vcr_c.use_cassette("assets/create_deposit_address.yaml")
# def test_get_assets(white_bit_client: WhiteBITClient):
#     assets = white_bit_client.create_deposit_address("USDT", "ERC20")


# @vcr_c.use_cassette("assets/create_deposit_address.yaml")
# async def test_async_get_assets(white_bit_client: WhiteBITClient):
#     assets = await white_bit_client.async_create_deposit_address("USDT", "ERC20")
