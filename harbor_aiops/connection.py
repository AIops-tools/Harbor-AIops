"""Harbor v2 REST client, with bounded pagination and explicit errors."""

from __future__ import annotations

import atexit
import threading
from typing import Any
from urllib.parse import quote

import httpx

from harbor_aiops.config import AppConfig, TargetConfig, load_config


class HarborApiError(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.status_code = status_code
        super().__init__(message)


def segment(value: str | int) -> str:
    text = str(value)
    if not text or text in (".", "..") or "/" in text:
        raise ValueError("Invalid Harbor path segment.")
    return quote(text, safe="")


class HarborConnection:
    def __init__(self, target: TargetConfig, client: Any | None = None) -> None:
        self.target = target
        self._client = client or httpx.Client(
            base_url=target.base_url.rstrip("/") + "/",
            auth=httpx.BasicAuth(target.username, target.password),
            verify=target.verify,
            timeout=target.timeout,
            headers={"Accept": "application/json"},
        )

    def close(self) -> None:
        self._client.close()

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        if not path.startswith("/") or ".." in path.split("/"):
            raise ValueError("Harbor API path must be absolute and stay under /api/v2.0.")
        try:
            response = self._client.get(path.lstrip("/"), params=params)
        except httpx.ConnectTimeout as exc:
            raise HarborApiError(
                f"Could not connect to Harbor {self.target.host} within {self.target.timeout:g}s."
            ) from exc
        except httpx.TimeoutException as exc:
            raise HarborApiError(
                f"Harbor request timed out after {self.target.timeout:g}s; check server load."
            ) from exc
        except httpx.HTTPError as exc:
            raise HarborApiError(
                f"Harbor request failed: {type(exc).__name__}; check network and TLS."
            ) from exc
        if response.status_code >= 400:
            reason = {
                401: "credentials rejected",
                403: "account lacks permission",
                404: "resource not found",
            }.get(response.status_code, "request rejected")
            raise HarborApiError(
                f"Harbor {reason} ({response.status_code}) for {path}.", response.status_code
            )
        try:
            return response.json()
        except ValueError as exc:
            raise HarborApiError(f"Harbor returned non-JSON data for {path}.") from exc

    def list(self, path: str, *, limit: int = 50, params: dict[str, Any] | None = None) -> dict:
        if not 1 <= limit <= 500:
            raise ValueError("limit must be between 1 and 500.")
        items: list[Any] = []
        size = min(100, limit + 1)
        page = 1
        while len(items) <= limit:
            query = dict(params or {})
            query.update({"page": page, "page_size": size})
            batch = self.get(path, query)
            if not isinstance(batch, list):
                raise HarborApiError(
                    f"Harbor returned a non-list for {path}; cannot claim an empty page."
                )
            if len(batch) > size:
                raise HarborApiError(f"Harbor returned more than page_size={size} for {path}.")
            items.extend(batch)
            if len(batch) < size:
                break
            page += 1
        return {
            "items": items[:limit],
            "returned": min(len(items), limit),
            "limit": limit,
            "truncated": len(items) > limit,
        }


class ConnectionManager:
    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or load_config()
        self._connections: dict[str, HarborConnection] = {}
        self._lock = threading.Lock()
        atexit.register(self.close)

    def connect(self, target: str | None = None) -> HarborConnection:
        chosen = self.config.get_target(target)
        with self._lock:
            if chosen.name not in self._connections:
                self._connections[chosen.name] = HarborConnection(chosen)
            return self._connections[chosen.name]

    def close(self) -> None:
        with self._lock:
            for connection in self._connections.values():
                connection.close()
            self._connections.clear()
