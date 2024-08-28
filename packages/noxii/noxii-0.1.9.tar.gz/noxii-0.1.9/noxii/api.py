import os
from datetime import date, datetime
from typing import overload

import httpx
from dotenv import load_dotenv

from .errors import GuildNotFound, InvalidAPIKey, NoGuildAccess, NotFound, UserNotFound
from .models import Database


def _stats_dict(data: dict[str, int]) -> dict[date, int]:
    return {datetime.strptime(d, "%Y-%m-%d").date(): count for d, count in data.items()}


class NoxiiAPI:
    def __init__(self, api_key: str | None = None, httpx_client: httpx.Client | None = None):
        self._httpx_client: httpx.Client | None = httpx_client

        if httpx_client is None:
            self._httpx_client = httpx.Client()
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("NOXII_KEY")
            if api_key is None:
                raise InvalidAPIKey(
                    "Please provide an API key or set the API_KEY environment variable."
                )

        self._header = {"key": api_key, "accept": "application/json"}

    def test(self):
        print("Success!")

    @overload
    def _get(self, endpoint: str) -> dict: ...

    @overload
    def _get(self, endpoint: str, stream: bool) -> bytes: ...

    def _get(self, endpoint: str, stream: bool = False):
        response = self._httpx_client.get(
            f"http://api.aenoxic.de/noxii/v1/{endpoint}", headers=self._header
        )

        if response.status_code == 401:
            raise InvalidAPIKey()
        elif response.status_code == 403:
            raise NoGuildAccess()
        elif response.status_code == 404:
            response = response.json()
            message = response.get("detail")
            if "user" in message.lower() or "member" in message.lower():
                raise UserNotFound()
            elif "guild" in message.lower():
                raise GuildNotFound
            raise NotFound()

        if stream:
            return response.read()

        return response.json()

    def get_user_stats(self, user_id: int):
        data = self._get(f"user/{user_id}")
        return data
