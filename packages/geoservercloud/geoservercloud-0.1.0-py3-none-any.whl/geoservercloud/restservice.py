from typing import Any

import requests


class RestService:
    def __init__(self, url: str, auth: tuple[str, str]) -> None:
        self.url: str = url
        self.auth: tuple[str, str] = auth

    def get(
        self,
        path: str,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        response: requests.Response = requests.get(
            f"{self.url}{path}",
            params=params,
            headers=headers,
            auth=self.auth,
        )
        if response.status_code != 404:
            response.raise_for_status()
        return response

    def post(
        self,
        path: str,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        json: dict[str, dict[str, Any]] | None = None,
        data: bytes | None = None,
    ) -> requests.Response:

        response: requests.Response = requests.post(
            f"{self.url}{path}",
            params=params,
            headers=headers,
            json=json,
            data=data,
            auth=self.auth,
        )
        if response.status_code != 409:
            response.raise_for_status()
        return response

    def put(
        self,
        path: str,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        json: dict[str, dict[str, Any]] | None = None,
        data: bytes | None = None,
    ) -> requests.Response:
        response: requests.Response = requests.put(
            f"{self.url}{path}",
            params=params,
            headers=headers,
            json=json,
            data=data,
            auth=self.auth,
        )
        response.raise_for_status()
        return response

    def delete(
        self,
        path: str,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        response: requests.Response = requests.delete(
            f"{self.url}{path}",
            params=params,
            headers=headers,
            auth=self.auth,
        )
        if response.status_code != 404:
            response.raise_for_status()
        return response
