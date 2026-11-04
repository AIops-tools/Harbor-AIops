"""Shared Harbor MCP server and sanitized error handling."""

from __future__ import annotations

import functools
import logging
import threading
from collections.abc import Callable
from typing import Any, Optional

import httpx
from mcp.server import MCPServer

from harbor_aiops import __version__
from harbor_aiops.connection import ConnectionManager, HarborApiError, HarborWriteUncertainError
from harbor_aiops.governance import mark_unknown, sanitize
from harbor_aiops.secretstore import SecretStoreError

logger = logging.getLogger(__name__)
_ERROR_MAX = 800
_UNDETERMINED_ERRORS = (
    httpx.ReadTimeout,
    httpx.WriteTimeout,
    httpx.ReadError,
    httpx.WriteError,
    httpx.RemoteProtocolError,
)


def _safe_error(exc: Exception, tool: str) -> str:
    logger.error("Tool %s failed", tool, exc_info=True)
    if isinstance(
        exc,
        (
            HarborApiError,
            ValueError,
            KeyError,
            FileNotFoundError,
            PermissionError,
            SecretStoreError,
            OSError,
        ),
    ):
        return sanitize(str(exc), _ERROR_MAX)
    return f"{type(exc).__name__}: operation failed."


def tool_errors(shape: str = "dict") -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as exc:  # noqa: BLE001 — sanitized below
                payload = {
                    "error": _safe_error(exc, func.__name__),
                    "hint": "Run 'harbor-aiops doctor' to check target and permissions.",
                }
                return mark_unknown(payload) if isinstance(
                    exc, (*_UNDETERMINED_ERRORS, HarborWriteUncertainError)
                ) else payload

        return wrapper

    return decorator


mcp = MCPServer(
    "harbor-aiops",
    version=__version__,
    instructions=(
        "Governed Harbor registry operations: health, volume, GC, replication and "
        "retention diagnosis. Every tool is audited and budgeted."
    ),
)

_manager: Optional[ConnectionManager] = None
_lock = threading.Lock()


def _get_connection(target: Optional[str] = None) -> Any:
    global _manager  # noqa: PLW0603
    with _lock:
        if _manager is None:
            _manager = ConnectionManager()
        manager = _manager
    return manager.connect(target)
