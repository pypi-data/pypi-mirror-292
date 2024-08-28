from conftest import vcr_c  # noqa
from whitebit_httpx_client import WhiteBITClient  # noqa


@vcr_c.use_cassette("assets/get_deposit_withdraw_history.yaml")
def test_sync_get_deposit_withdraw_history(white_bit_client: WhiteBITClient):
    result = white_bit_client.get_deposit_withdraw_history()
    assert "records" in result.keys()


@vcr_c.use_cassette("assets/get_deposit_withdraw_history.yaml")
def test_sync_get_deposit_withdraw_history_by_address(white_bit_client: WhiteBITClient):
    result = white_bit_client.get_deposit_withdraw_history(
        address="TYTd64XYig1tH767Z8hAiDqML66zNwo3fD"
    )
    assert "records" in result.keys()
    assert (
        result["total"] == 1
    )  # We had only one top up from that address when created test case


@vcr_c.use_cassette("assets/get_deposit_withdraw_history.yaml")
async def test_async_get_deposit_withdraw_history(white_bit_client: WhiteBITClient):
    result = await white_bit_client.async_get_deposit_withdraw_history()
    assert "records" in result.keys()


@vcr_c.use_cassette("assets/get_deposit_withdraw_history.yaml")
async def test_async_get_deposit_withdraw_history_by_address(
    white_bit_client: WhiteBITClient,
):
    result = await white_bit_client.async_get_deposit_withdraw_history(
        address="TYTd64XYig1tH767Z8hAiDqML66zNwo3fD"
    )
    assert "records" in result.keys()
    assert (
        result["total"] == 1
    )  # We had only one top up from that address when created test case
