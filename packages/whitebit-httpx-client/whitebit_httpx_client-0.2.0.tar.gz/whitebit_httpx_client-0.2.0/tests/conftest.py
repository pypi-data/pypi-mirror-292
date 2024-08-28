import json
import logging
import os

import pytest
import vcr

from whitebit_httpx_client import WhiteBITClient

# ALL = "all"
# ANY = "any"
# NEW_EPISODES = "new_episodes"
# NONE = "none"
# ONCE = "once"

WHITE_BIT_API_KEY = os.getenv("WHITE_BIT_API_KEY")
WHITE_BIT_SECRET_KEY = os.getenv("WHITE_BIT_SECRET_KEY")


def body_matcher(r1, r2):
    try:
        r1_body = json.loads(r1.body.decode("utf-8"))
        r2_body = json.loads(r2.body.decode("utf-8"))
        r1_body.pop("nonce")
        r2_body.pop("nonce")
    except (ValueError, AttributeError):
        return r1.body == r2.body
    return r1_body == r2_body


logging.getLogger("vcr").setLevel(logging.WARNING)
vcr_c = vcr.VCR(
    cassette_library_dir="tests/fixtures/cassettes",
    record_mode=os.environ.get("VCR_RECORD_MODE", "none"),
    match_on=["host", "path", "method", "query", "body"],
    filter_headers=[
        "Authorization",
        "Cookie",
        "Date",
        "X-API-Key",
        "x-txc-signature",
        "x-txc-apikey",
    ],
)

vcr_c.register_matcher("body", body_matcher)


@pytest.fixture
def white_bit_client() -> WhiteBITClient:
    return WhiteBITClient(
        api_public_key=WHITE_BIT_API_KEY, api_secret_key=WHITE_BIT_SECRET_KEY
    )
