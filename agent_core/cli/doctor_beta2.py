from __future__ import annotations

from pathlib import Path

import typer

from agent_core.stabilization.beta2_doctor import (
    doctor_agent_layers,
    format_beta2_doctor_text,
)


app = typer.Typer(help="Doctor checks for existing RAG, memory, and provider layers.")


@app.command("agent")
def doctor_agent(
    path: Path = typer.Argument(..., help="Path to an agent YAML file."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Validate provider, memory, and knowledge/RAG settings for one agent."""

    result = doctor_agent_layers(path)

    if json_output:
        typer.echo(result.to_json())
    else:
        typer.echo(format_beta2_doctor_text(result))

    if not result.ok:
        raise typer.Exit(code=1)
