"""Harbor AIops command line interface."""

from __future__ import annotations

import json
import sys
from typing import Annotated

import typer

from harbor_aiops.cli._common import (
    cli_errors,
    console,
    double_confirm,
    governed,
    print_truncation_note,
)
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


@app.command("statistics")
@cli_errors
def statistics(target: Target = None) -> None:
    """Show registry-wide project and repository counts."""
    from harbor_aiops.mcp_server.tools.registry import harbor_statistics
    _print(harbor_statistics(target=target))


@app.command("project-members")
@cli_errors
def project_members(project: str, limit: Limit = 50, target: Target = None) -> None:
    """List members of a Harbor project."""
    from harbor_aiops.mcp_server.tools.registry import harbor_project_members
    _print(harbor_project_members(project=project, limit=limit, target=target), "members")


@app.command("immutable-rules")
@cli_errors
def immutable_rules(project: str, limit: Limit = 50, target: Target = None) -> None:
    """List tag immutability rules for a project."""
    from harbor_aiops.mcp_server.tools.registry import harbor_immutable_rules
    _print(harbor_immutable_rules(project=project, limit=limit, target=target), "rules")


@app.command("robot-accounts")
@cli_errors
def robot_accounts(limit: Limit = 50, target: Target = None) -> None:
    """List robot accounts without exposing their secrets."""
    from harbor_aiops.mcp_server.tools.registry import harbor_robot_accounts
    _print(harbor_robot_accounts(limit=limit, target=target), "robot accounts")


@app.command("labels")
@cli_errors
def labels(limit: Limit = 50, target: Target = None) -> None:
    """List Harbor labels."""
    from harbor_aiops.mcp_server.tools.registry import harbor_labels
    _print(harbor_labels(limit=limit, target=target), "labels")


@app.command("scan-all-metrics")
@cli_errors
def scan_all_metrics(target: Target = None) -> None:
    """Show latest registry-wide scan metrics."""
    from harbor_aiops.mcp_server.tools.registry import harbor_scan_all_metrics
    _print(harbor_scan_all_metrics(target=target))


@app.command("scheduled-scan-metrics")
@cli_errors
def scheduled_scan_metrics(target: Target = None) -> None:
    """Show latest scheduled scan metrics."""
    from harbor_aiops.mcp_server.tools.registry import harbor_scheduled_scan_metrics
    _print(harbor_scheduled_scan_metrics(target=target))


@app.command("scan-log")
@cli_errors
def scan_log(project: str, repository: str, reference: str, report_id: str,
             target: Target = None) -> None:
    """Show a bounded artifact scan report log."""
    from harbor_aiops.mcp_server.tools.registry import harbor_scan_log
    _print(harbor_scan_log(project=project, repository=repository, reference=reference,
                           report_id=report_id, target=target))


@app.command("projects")
@cli_errors
def projects(limit: Limit = 50, target: Target = None) -> None:
    """List Harbor projects."""
    from harbor_aiops.mcp_server.tools.registry import harbor_projects
    _print(harbor_projects(limit=limit, target=target), "projects")


@app.command("project")
@cli_errors
def project(name: str, target: Target = None) -> None:
    """Show one Harbor project."""
    from harbor_aiops.mcp_server.tools.registry import harbor_project
    _print(harbor_project(name=name, target=target))


@app.command("project-summary")
@cli_errors
def project_summary(name: str, target: Target = None) -> None:
    """Show Harbor's project usage summary."""
    from harbor_aiops.mcp_server.tools.registry import harbor_project_summary
    _print(harbor_project_summary(name=name, target=target))


@app.command("repositories")
@cli_errors
def repositories(project: str, limit: Limit = 50, target: Target = None) -> None:
    """List repositories in a project."""
    from harbor_aiops.mcp_server.tools.registry import harbor_repositories
    _print(harbor_repositories(project=project, limit=limit, target=target), "repositories")


@app.command("artifacts")
@cli_errors
def artifacts(project: str, repository: str, limit: Limit = 50, target: Target = None) -> None:
    """List artifacts in a repository."""
    from harbor_aiops.mcp_server.tools.registry import harbor_artifacts
    _print(harbor_artifacts(project=project, repository=repository, limit=limit,
                            target=target), "artifacts")


@app.command("artifact")
@cli_errors
def artifact(project: str, repository: str, reference: str, target: Target = None) -> None:
    """Show one artifact by digest or tag."""
    from harbor_aiops.mcp_server.tools.registry import harbor_artifact
    _print(harbor_artifact(project=project, repository=repository, reference=reference,
                           target=target))


@app.command("tags")
@cli_errors
def tags(project: str, repository: str, reference: str, limit: Limit = 50,
         target: Target = None) -> None:
    """List artifact tags."""
    from harbor_aiops.mcp_server.tools.registry import harbor_tags
    _print(harbor_tags(project=project, repository=repository, reference=reference,
                       limit=limit, target=target), "tags")


@app.command("vulnerabilities")
@cli_errors
def vulnerabilities(project: str, repository: str, reference: str,
                    target: Target = None) -> None:
    """Show an artifact's stored vulnerability report."""
    from harbor_aiops.mcp_server.tools.registry import harbor_vulnerabilities
    _print(harbor_vulnerabilities(project=project, repository=repository,
                                  reference=reference, target=target))


@app.command("replication-policies")
@cli_errors
def replication_policies(limit: Limit = 50, target: Target = None) -> None:
    """List replication policies."""
    from harbor_aiops.mcp_server.tools.registry import harbor_replication_policies
    _print(harbor_replication_policies(limit=limit, target=target), "replication policies")


@app.command("replication-policy")
@cli_errors
def replication_policy(policy_id: int, target: Target = None) -> None:
    """Show a replication policy."""
    from harbor_aiops.mcp_server.tools.registry import harbor_replication_policy
    _print(harbor_replication_policy(policy_id=policy_id, target=target))


@app.command("replication-execution")
@cli_errors
def replication_execution(execution_id: int, target: Target = None) -> None:
    """Show one replication execution."""
    from harbor_aiops.mcp_server.tools.registry import harbor_replication_execution
    _print(harbor_replication_execution(execution_id=execution_id, target=target))


@app.command("retention-tasks")
@cli_errors
def retention_tasks(policy_id: int, execution_id: int, limit: Limit = 50,
                    target: Target = None) -> None:
    """List tasks of a retention execution."""
    from harbor_aiops.mcp_server.tools.registry import harbor_retention_tasks
    _print(harbor_retention_tasks(policy_id=policy_id, execution_id=execution_id,
                                  limit=limit, target=target), "retention tasks")


@app.command("quotas")
@cli_errors
def quotas(limit: Limit = 50, target: Target = None) -> None:
    """List Harbor quotas."""
    from harbor_aiops.mcp_server.tools.registry import harbor_quotas
    _print(harbor_quotas(limit=limit, target=target), "quotas")


@app.command("project-audit-logs")
@cli_errors
def project_audit_logs(project: str, limit: Limit = 50, target: Target = None) -> None:
    """List Harbor audit logs for a project."""
    from harbor_aiops.mcp_server.tools.registry import harbor_project_audit_logs
    _print(harbor_project_audit_logs(project=project, limit=limit, target=target), "audit logs")


@app.command("scan-artifact")
@cli_errors
def scan_artifact(project: str, repository: str, reference: str,
                  dry_run: bool = False, target: Target = None) -> None:
    """Request a Harbor artifact vulnerability scan."""
    from harbor_aiops.mcp_server.tools.writes import harbor_scan_artifact
    if not dry_run:
        double_confirm("scan artifact", f"{project}/{repository}:{reference}")
    _print(harbor_scan_artifact(project=project, repository=repository,
                                reference=reference, dry_run=dry_run, target=target))


@app.command("create-tag")
@cli_errors
def create_tag(project: str, repository: str, reference: str, tag: str,
               dry_run: bool = False, target: Target = None) -> None:
    """Create and verify a Harbor artifact tag."""
    from harbor_aiops.mcp_server.tools.writes import harbor_create_tag
    if not dry_run:
        double_confirm("create tag", f"{project}/{repository}:{tag}")
    _print(harbor_create_tag(project=project, repository=repository, reference=reference,
                             tag=tag, dry_run=dry_run, target=target))


@app.command("gc-execution")
@cli_errors
def gc_execution(gc_id: int, target: Target = None) -> None:
    """Show one GC execution."""
    from harbor_aiops.mcp_server.tools.registry import harbor_gc_execution
    _print(harbor_gc_execution(gc_id=gc_id, target=target))


@app.command("gc-log")
@cli_errors
def gc_log(gc_id: int, target: Target = None) -> None:
    """Show a bounded GC execution log."""
    from harbor_aiops.mcp_server.tools.registry import harbor_gc_log
    _print(harbor_gc_log(gc_id=gc_id, target=target))


@app.command("replication-task-log")
@cli_errors
def replication_task_log(execution_id: int, task_id: int, target: Target = None) -> None:
    """Show a bounded replication task log."""
    from harbor_aiops.mcp_server.tools.registry import harbor_replication_task_log
    _print(harbor_replication_task_log(execution_id=execution_id, task_id=task_id,
                                       target=target))


@app.command("retention-task-log")
@cli_errors
def retention_task_log(policy_id: int, execution_id: int, task_id: int,
                       target: Target = None) -> None:
    """Show a bounded retention task log."""
    from harbor_aiops.mcp_server.tools.registry import harbor_retention_task_log
    _print(harbor_retention_task_log(policy_id=policy_id, execution_id=execution_id,
                                     task_id=task_id, target=target))


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
