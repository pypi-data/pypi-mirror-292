import base64
import hashlib
import hmac
import json
from unittest.mock import patch

import pytest

from whitebit_httpx_client import (
    WhiteBITClient,  # Replace 'your_module' with the actual module name
)


@pytest.fixture
def client():
    return WhiteBITClient(
        api_public_key="test_public_key", api_secret_key="test_secret_key"
    )


def test_init(client):
    assert client.api_public_key == "test_public_key"
    assert client.api_secret_key == "test_secret_key"
    assert client.domain == "https://whitebit.com"


def test_prepare_request_data(client):
    with patch("time.time_ns", return_value=1000000000000):
        data = client._prepare_request_data(
            "/test/path", param1="value1", param2="value2"
        )
        assert data == {
            "request": "/test/path",
            "nonce": 1000000,  # This is now correct: 1000000000000 // 1_000_000
            "nonceWindow": True,
            "param1": "value1",
            "param2": "value2",
        }


def test_get_req_headers(client):
    prepared_data = client._prepare_request_data(
        request_path="/api/v4/main-account/create-new-address",
        param1="value1",
        param2="value2",
    )
    headers = client.get_req_headers(prepared_data)

    # Check if all required headers are present
    assert "Content-type" in headers
    assert "X-TXC-APIKEY" in headers
    assert "X-TXC-PAYLOAD" in headers
    assert "X-TXC-SIGNATURE" in headers

    # Check header values
    assert headers["Content-type"] == "application/json"
    assert headers["X-TXC-APIKEY"] == "test_public_key"

    # Verify payload
    decoded_payload = base64.b64decode(headers["X-TXC-PAYLOAD"]).decode("ascii")
    assert json.loads(decoded_payload) == prepared_data

    # Verify signature
    expected_signature = hmac.new(
        "test_secret_key".encode("ascii"),
        headers["X-TXC-PAYLOAD"].encode("ascii"),
        hashlib.sha512,
    ).hexdigest()
    assert headers["X-TXC-SIGNATURE"] == expected_signature


def test_get_req_headers_different_data(client):
    test_data1 = {"request": "/path1", "nonce": 1000000, "nonceWindow": True}
    test_data2 = {"request": "/path2", "nonce": 1000001, "nonceWindow": True}

    headers1 = client.get_req_headers(test_data1)
    headers2 = client.get_req_headers(test_data2)

    assert headers1["X-TXC-PAYLOAD"] != headers2["X-TXC-PAYLOAD"]
    assert headers1["X-TXC-SIGNATURE"] != headers2["X-TXC-SIGNATURE"]
