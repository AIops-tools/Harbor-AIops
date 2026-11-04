"""Harbor target configuration; passwords remain in the encrypted secret store."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml

from harbor_aiops.governance.paths import ops_home
from harbor_aiops.secretstore import MasterPasswordError, SecretStoreError, get_secret, has_store

CONFIG_FILE = ops_home() / "config.yaml"
SECRET_ENV_PREFIX = "HARBOR_"  # nosec B105 — variable name
SECRET_ENV_SUFFIX = "_PASSWORD"  # nosec B105 — variable name


def _secret_env_key(name: str) -> str:
    return f"{SECRET_ENV_PREFIX}{name.upper().replace('-', '_')}{SECRET_ENV_SUFFIX}"


def _resolve_secret(name: str) -> str:
    if has_store():
        try:
            return get_secret(name)
        except MasterPasswordError:
            raise
        except SecretStoreError:
            pass
    value = os.environ.get(_secret_env_key(name))
    if value:
        return value
    raise OSError(f"No password for Harbor target '{name}'. Run 'harbor-aiops secret set {name}'.")


@dataclass(frozen=True)
class TargetConfig:
    name: str
    host: str
    username: str
    scheme: str = "https"
    port: int = 443
    verify_ssl: bool = True
    ca_file: str | None = None
    timeout: float = 30.0

    def __post_init__(self) -> None:
        if self.scheme not in ("https", "http"):
            raise ValueError("scheme must be 'https' or 'http'.")
        if not self.host or "/" in self.host or "@" in self.host:
            raise ValueError("host must be a hostname or IP address without a path or credentials.")
        if not self.username:
            raise ValueError("username is required for Harbor API access.")
        if not 1 <= self.port <= 65535 or self.timeout <= 0:
            raise ValueError("port must be 1–65535 and timeout must be positive.")
        if self.scheme == "http" and not self.host.startswith(("localhost", "127.0.0.1", "[::1]")):
            raise ValueError("Plain HTTP Basic authentication is allowed only for a local lab.")

    @property
    def base_url(self) -> str:
        return f"{self.scheme}://{self.host}:{self.port}/api/v2.0"

    @property
    def verify(self) -> bool | str:
        return self.ca_file or True if self.verify_ssl else False

    @property
    def password(self) -> str:
        return _resolve_secret(self.name)


@dataclass(frozen=True)
class AppConfig:
    targets: tuple[TargetConfig, ...] = ()

    def get_target(self, name: str | None = None) -> TargetConfig:
        if name is None:
            if not self.targets:
                raise ValueError("No Harbor targets configured. Run 'harbor-aiops init'.")
            return self.targets[0]
        for target in self.targets:
            if target.name == name:
                return target
        raise KeyError(f"Unknown Harbor target '{name}'.")


def load_config(path: Path | None = None) -> AppConfig:
    path = path or Path(os.environ.get("HARBOR_AIOPS_CONFIG", CONFIG_FILE))
    if not path.is_file():
        raise FileNotFoundError(f"No Harbor config at {path}. Run 'harbor-aiops init'.")
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict) or not isinstance(raw.get("targets"), list):
        raise ValueError("Harbor config must contain a targets list.")
    return AppConfig(tuple(TargetConfig(**entry) for entry in raw["targets"]))
