"""CLI Harbor reads call the same governed MCP functions."""

import ast
from pathlib import Path

from typer.testing import CliRunner


def test_harbor_read_commands_delegate_to_mcp_tools():
    path = Path(__file__).parents[1] / "harbor_aiops/cli/_root.py"
    tree = ast.parse(path.read_text())
    commands = {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and any(
            isinstance(d, ast.Call)
            and isinstance(d.func, ast.Attribute)
            and d.func.attr == "command"
            for d in node.decorator_list
        )
    }
    reads = {
        "health",
        "volumes",
        "gc",
        "replication",
        "replication_tasks",
        "retention",
        "retention_executions",
        "diagnose",
        "doctor",
    }
    assert reads <= commands.keys()
    for name in reads:
        imports = [node for node in ast.walk(commands[name]) if isinstance(node, ast.ImportFrom)]
        assert any(
            (node.module or "").startswith("harbor_aiops.mcp_server.tools") for node in imports
        )


def test_cli_help_lists_harbor_operations():
    from harbor_aiops.cli import app

    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    for command in ("health", "gc", "replication", "retention", "diagnose"):
        assert command in result.output
