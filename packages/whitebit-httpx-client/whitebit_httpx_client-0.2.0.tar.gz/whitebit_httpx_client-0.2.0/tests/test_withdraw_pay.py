from conftest import vcr_c  # noqa
from whitebit_httpx_client import WhiteBITClient  # noqa

WITHDRAWAL_UUID = "95fb1fe9-4626-4842-9e86-383849ce8120"
CHOCK_WB_NEAR_USDT_ADDRESS = (
    "7b22571598a94549165ce860597b033158e1821fb6b033679fcb02a986c8c520"
)


@vcr_c.use_cassette("withdraw/withdraw_pay.yaml")
def test_sync_withdraw_pay(white_bit_client: WhiteBITClient):
    _ = white_bit_client.withdraw_pay(
        "USDT", "NEAR", "5", CHOCK_WB_NEAR_USDT_ADDRESS, WITHDRAWAL_UUID
    )


@vcr_c.use_cassette("withdraw/withdraw_pay.yaml")
def test_async_withdraw_pay(white_bit_client: WhiteBITClient):
    _ = white_bit_client.async_withdraw_pay(
        "USDT", "NEAR", "5", CHOCK_WB_NEAR_USDT_ADDRESS, WITHDRAWAL_UUID
    )
