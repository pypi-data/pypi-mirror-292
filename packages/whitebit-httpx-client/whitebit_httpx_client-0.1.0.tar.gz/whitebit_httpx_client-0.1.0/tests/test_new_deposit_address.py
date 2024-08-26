from conftest import vcr_c  # noqa
import pytest
from whitebit_httpx_client import WhiteBITClient  # noqa
import httpx


@vcr_c.use_cassette("assets/create_deposit_address.yaml")
def test_sync_create_deposit_address(white_bit_client: WhiteBITClient):
    result = white_bit_client.create_deposit_address("USDT", "ERC20")
    assert "account" in result.keys()
    assert "address" in result["account"]


@vcr_c.use_cassette("assets/create_deposit_address.yaml")
async def test_async_create_deposit_address(white_bit_client: WhiteBITClient):
    result = await white_bit_client.async_create_deposit_address("USDT", "ERC20")
    assert "account" in result.keys()
    assert "address" in result["account"]


@vcr_c.use_cassette("assets/create_deposit_address.yaml")
async def test_async_create_deposit_address_fiat(white_bit_client: WhiteBITClient):
    with pytest.raises(httpx.HTTPStatusError):
        _ = await white_bit_client.async_create_deposit_address("USD", "ERC20")


@vcr_c.use_cassette("assets/create_deposit_address.yaml")
async def test_async_create_deposit_address_wrong_ticket(
    white_bit_client: WhiteBITClient,
):
    with pytest.raises(httpx.HTTPStatusError):
        _ = await white_bit_client.async_create_deposit_address("UbSD", "ERC20")
