"""Entrada da CLI. `list` funciona; `generate` checa precos e (por ora) sai - otimizadores nos Blocos 4/5."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from ..core.pricing import PriceError, assert_prices_usable
from ..disclaimer import DISCLAIMER
from ..games import registry

app = typer.Typer(help="Lottery Optimization Engine - otimiza cobertura, nao preve sorteios.")
console = Console()


@app.command("list")
def list_games() -> None:
    """Lista as loterias disponiveis."""
    table = Table(title="Loterias")
    for col in ("game_id", "nome", "universo", "sorteio", "tamanhos", "preco"):
        table.add_column(col)
    for game_id in registry.available():
        s = registry.get(game_id)
        table.add_row(game_id, s.name, f"{s.universe_min}-{s.universe_max}", str(s.draw_size),
                      f"{s.min_ticket_size}-{s.max_ticket_size}", s.price_status)
    console.print(table)


@app.command("generate")
def generate(
    game: str,
    tickets: int = 10,
    size: int = 0,
    seed: int = 12345,
    allow_example_prices: bool = typer.Option(False, "--allow-example-prices"),
) -> None:
    """Gera uma carteira. Bloqueia se os precos nao forem oficiais (salvo --allow-example-prices)."""
    console.print(f"[yellow]{DISCLAIMER}[/yellow]")
    spec = registry.get(game)
    try:
        assert_prices_usable(spec, allow_example=allow_example_prices)
    except PriceError as e:
        console.print(f"[red]Bloqueado:[/red] {e}")
        raise typer.Exit(code=2) from None
    console.print("[yellow]Otimizadores ainda nao implementados (Blocos 4/5).[/yellow]")
    raise typer.Exit(code=1)


def main() -> None:  # pragma: no cover - entrypoint
    app()


if __name__ == "__main__":  # pragma: no cover
    app()
