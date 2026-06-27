"""Entrada da CLI. `list` ja funciona; `generate` sera ligado quando os otimizadores chegarem."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from ..disclaimer import DISCLAIMER
from ..games import registry

app = typer.Typer(help="Lottery Optimization Engine - otimiza cobertura, nao preve sorteios.")
console = Console()


@app.command("list")
def list_games() -> None:
    """Lista as loterias disponiveis."""
    table = Table(title="Loterias")
    table.add_column("game_id")
    table.add_column("nome")
    table.add_column("universo")
    table.add_column("sorteio")
    table.add_column("tamanhos")
    for game_id in registry.available():
        s = registry.get(game_id)
        table.add_row(
            game_id, s.name, f"{s.universe_min}-{s.universe_max}", str(s.draw_size),
            f"{s.min_ticket_size}-{s.max_ticket_size}",
        )
    console.print(table)


@app.command("generate")
def generate(game: str, tickets: int = 10, size: int = 0, seed: int = 12345) -> None:
    """Gera uma carteira (sera ligado quando os otimizadores forem implementados)."""
    console.print(f"[yellow]{DISCLAIMER}[/yellow]")
    raise typer.Exit(code=1)  # geracao real chega nos Blocos 4/5


def main() -> None:  # pragma: no cover - entrypoint
    app()
