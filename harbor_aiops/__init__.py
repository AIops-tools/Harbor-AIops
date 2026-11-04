"""Harbor AIops: governed container registry operations for AI agents."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("harbor-aiops")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"
