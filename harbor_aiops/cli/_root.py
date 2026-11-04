"""Harbor AIops command line interface."""

from __future__ import annotations

import json
import sys
from typing import Annotated

import typer

from harbor_aiops.cli._common import cli_errors, console, governed, print_truncation_note
from harbor_aiops.cli.secret import secret_app
from harbor_aiops.cli.undo import undo_app
from harbor_aiops.governance.paths import ops_home

app = typer.Typer(
    name="harbor-aiops",
    no_args_is_help=True,
    help="Audited Harbor registry diagnosis and maintenance visibility.",
)
app.add_typer(secret_app, name="secret")
app.add_typer(undo_app, name="undo")

Target = Annotated[str | None, typer.Option("--target", "-t", help="Configured Harbor target")]
Limit = Annotated[int, typer.Option("--limit", help="Max records, 1–500")]


def _print(result: dict, noun: str = "records") -> None:
    result = governed(result)
    console.print_json(json.dumps(result))
    print_truncation_note(result, noun)


@app.command("init")
@cli_errors
def init() -> None:
    """Add a Harbor target and store its password encrypted."""
    import getpass
    from pathlib import Path

    import yaml

    from harbor_aiops.config import TargetConfig
    from harbor_aiops.secretstore import SecretStore, resolve_master_password

    name = typer.prompt("Target name", default="harbor")
    host = typer.prompt("Harbor hostname")
    username = typer.prompt("Harbor username or robot account")
    ca_file = typer.prompt("Custom CA PEM path (optional)", default="")
    chosen = TargetConfig(name=name, host=host, username=username, ca_file=ca_file or None)
    path = Path(ops_home()) / "config.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise ValueError(f"Config already exists at {path}; edit it to add a target.")
    master = resolve_master_password(confirm_if_new=True)
    password = getpass.getpass("Harbor password (hidden): ")
    SecretStore.unlock(master).set(name, password)
    path.write_text(
        yaml.safe_dump(
            {
                "targets": [
                    {
                        "name": chosen.name,
                        "host": chosen.host,
                        "username": chosen.username,
                        "scheme": chosen.scheme,
                        "port": chosen.port,
                        "verify_ssl": chosen.verify_ssl,
                        "ca_file": chosen.ca_file,
                        "timeout": chosen.timeout,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    path.chmod(0o600)
    console.print(f"[green]Configured '{name}' in {path}.[/]")


@app.command("health")
@cli_errors
def health(target: Target = None) -> None:
    """Show Harbor component health."""
    from harbor_aiops.mcp_server.tools.registry import harbor_health

    _print(harbor_health(target=target))


@app.command("volumes")
@cli_errors
def volumes(target: Target = None) -> None:
    """Show Harbor storage volume usage."""
    from harbor_aiops.mcp_server.tools.registry import harbor_volumes

    _print(harbor_volumes(target=target))


@app.command("gc")
@cli_errors
def gc(limit: Limit = 50, target: Target = None) -> None:
    """List garbage-collection executions."""
    from harbor_aiops.mcp_server.tools.registry import harbor_gc_history

    _print(harbor_gc_history(limit=limit, target=target), "GC executions")


@app.command("replication")
@cli_errors
def replication(limit: Limit = 50, status: str | None = None, target: Target = None) -> None:
    """List replication executions."""
    from harbor_aiops.mcp_server.tools.registry import harbor_replication_executions

    _print(
        harbor_replication_executions(limit=limit, status=status, target=target),
        "replication executions",
    )


@app.command("replication-tasks")
@cli_errors
def replication_tasks(execution_id: int, limit: Limit = 50, target: Target = None) -> None:
    """List tasks in one replication execution."""
    from harbor_aiops.mcp_server.tools.registry import harbor_replication_tasks

    _print(
        harbor_replication_tasks(execution_id=execution_id, limit=limit, target=target),
        "replication tasks",
    )


@app.command("retention")
@cli_errors
def retention(policy_id: int, target: Target = None) -> None:
    """Show a retention policy by ID."""
    from harbor_aiops.mcp_server.tools.registry import harbor_retention_policy

    _print(harbor_retention_policy(policy_id=policy_id, target=target))


@app.command("retention-executions")
@cli_errors
def retention_executions(policy_id: int, limit: Limit = 50, target: Target = None) -> None:
    """List executions of a retention policy."""
    from harbor_aiops.mcp_server.tools.registry import harbor_retention_executions

    _print(
        harbor_retention_executions(policy_id=policy_id, limit=limit, target=target),
        "retention executions",
    )


@app.command("diagnose")
@cli_errors
def diagnose(limit: Limit = 20, target: Target = None) -> None:
    """Correlate health, volume, GC and replication observations."""
    from harbor_aiops.mcp_server.tools.registry import harbor_diagnose

    _print(harbor_diagnose(limit=limit, target=target))


@app.command("doctor")
@cli_errors
def doctor(target: Target = None) -> None:
    """Test target configuration and Harbor health endpoint."""
    from harbor_aiops.mcp_server.tools.registry import harbor_health

    _print(harbor_health(target=target))


@app.command("mcp")
@cli_errors
def mcp_cmd() -> None:
    """Start the MCP server over stdio."""
    if sys.version_info < (3, 11):
        raise typer.Exit(2)
    from harbor_aiops.mcp_server.server import main

    main()


if __name__ == "__main__":
    app()
