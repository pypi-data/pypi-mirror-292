import base64
import hashlib
import hmac
import json
import time
from typing import Any, Dict

import httpx


class WhiteBITClient:
    domain = "https://whitebit.com"

    def __init__(self, api_public_key: str, api_secret_key: str):
        self.api_public_key = api_public_key
        self.api_secret_key = api_secret_key

    def get_req_headers(self, json_data: Dict[str, Any]) -> Dict[str, str]:
        data_json = json.dumps(json_data, separators=(",", ":"))
        payload = base64.b64encode(data_json.encode("ascii"))
        signature = hmac.new(
            self.api_secret_key.encode("ascii"), payload, hashlib.sha512
        ).hexdigest()

        return {
            "Content-type": "application/json",
            "X-TXC-APIKEY": self.api_public_key,
            "X-TXC-PAYLOAD": payload.decode("utf-8"),
            "X-TXC-SIGNATURE": signature,
        }

    def _prepare_request_data(self, request_path: str, **kwargs) -> Dict[str, Any]:
        data = {
            "request": request_path,
            "nonce": time.time_ns() // 1_000_000,
            "nonceWindow": True,
        }
        data.update(kwargs)
        return data

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        if response.status_code != 200:
            raise httpx.HTTPStatusError(
                f"Error connecting to Whitebit account: {response.text}",
                request=response.request,
                response=response,
            )
        return response.json()

    def create_deposit_address(self, ticker: str, network: str) -> Dict[str, Any]:
        request_path = "/api/v4/main-account/create-new-address"
        data = self._prepare_request_data(request_path, ticker=ticker, network=network)
        headers = self.get_req_headers(data)
        with httpx.Client() as client:
            response = client.post(
                self.domain + request_path, json=data, headers=headers
            )

        return self._handle_response(response)

    async def async_create_deposit_address(
        self, ticker: str, network: str
    ) -> Dict[str, Any]:
        request_path = "/api/v4/main-account/create-new-address"
        data = self._prepare_request_data(request_path, ticker=ticker, network=network)
        headers = self.get_req_headers(data)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.domain + request_path, json=data, headers=headers
            )

        return self._handle_response(response)

    def get_assets_data(self):
        request_path = "/api/v4/public/assets"
        with httpx.Client() as client:
            response = client.get(self.domain + request_path)
        return self._handle_response(response)

    async def async_get_assets_data(self):
        request_path = "/api/v4/public/assets"
        async with httpx.AsyncClient() as client:
            response = await client.get(self.domain + request_path)
        return self._handle_response(response)
