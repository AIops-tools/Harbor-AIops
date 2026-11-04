"""CLI package for harbor-aiops.

Re-exports ``app`` so the pyproject entry point
``harbor-aiops = "harbor_aiops.cli:app"`` works unchanged.
"""

from harbor_aiops.cli._root import app

__all__ = ["app"]
