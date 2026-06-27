"""CLI (Typer + Rich). Sempre imprime o aviso matematico; bloqueia preco de exemplo sem flag;
gera arquivos em output/YYYYMMDD_HHMMSS_GAME_ID/; registra config e logs."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ..algorithms import OPTIMIZERS, RuntimeConfig
from ..core.pricing import PriceError, assert_prices_usable, price_config_summary
from ..disclaimer import DISCLAIMER
from ..export import build_report, charts, export_csv, export_excel, export_report
from ..export.csv_exporter import load_csv
from ..generators import GENERATORS, GenerationConstraints
from ..games import registry
from ..metrics.scoring import PortfolioScore

app = typer.Typer(help="Lottery Optimization Engine - otimiza cobertura, NAO preve sorteios.")
console = Console()


def _notice() -> None:
    console.print(f"[yellow]{DISCLAIMER}[/yellow]\n")


def _run_dir(output_dir: str | None, game: str) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = Path(output_dir) if output_dir else Path("output")
    d = base / f"{ts}_{game}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _check_real_run(spec, allow_example: bool) -> None:
    """Bloqueia preco de EXEMPLO sem flag. Unset (sem preco) e ok no modo por contagem."""
    if spec.price_status == "example" and not allow_example:
        try:
            assert_prices_usable(spec, allow_example=False)
        except PriceError as e:
            console.print(f"[red]Bloqueado:[/red] {e}")
            raise typer.Exit(code=2) from None


def _constraints(ticket_size: int, mixed: str | None) -> GenerationConstraints:
    if mixed:
        sizes = tuple(int(x) for x in mixed.split(","))
        return GenerationConstraints(strategy="mixed_ticket_sizes", mixed_sizes=sizes)
    if ticket_size > 0:
        return GenerationConstraints(strategy="fixed", ticket_size=ticket_size)
    return GenerationConstraints(strategy="all_simple")


def _export_all(portfolio, spec, run_dir: Path, *, algorithm, seed, score_history=None, params=None):
    export_csv(portfolio, run_dir / "jogos.csv", game_id=spec.game_id)
    export_report(portfolio, spec, run_dir / "relatorio.txt", algorithm=algorithm, seed=seed,
                  params=params, timestamp=datetime.now().isoformat(timespec="seconds"),
                  score_history=score_history)
    export_excel(portfolio, run_dir / "jogos.xlsx", spec=spec, algorithm=algorithm, seed=seed,
                 score_history=score_history, params=params,
                 timestamp=datetime.now().isoformat(timespec="seconds"))
    charts.plot_frequency(portfolio, spec, run_dir / "frequencia_dezenas.png")
    charts.plot_overlap_distribution(portfolio, run_dir / "distribuicao_sobreposicao.png")
    charts.plot_coverage_by_subset(portfolio, spec, run_dir / "cobertura_por_subconjunto.png")
    if score_history:
        charts.plot_score_history(score_history, run_dir / "score_history.png")
    (run_dir / "config.log").write_text(
        f"game={spec.game_id}\nalgorithm={algorithm}\nseed={seed}\n"
        f"price_config={price_config_summary(spec)}\nparams={params}\n", encoding="utf-8")


@app.command("list-games")
def list_games() -> None:
    """Lista os jogos disponiveis."""
    _notice()
    table = Table(title="Loterias")
    for c in ("game_id", "nome", "universo", "sorteio", "tamanhos", "preco"):
        table.add_column(c)
    for gid in registry.available():
        s = registry.get(gid)
        table.add_row(gid, s.name, f"{s.universe_min}-{s.universe_max}", str(s.draw_size),
                      f"{s.min_ticket_size}-{s.max_ticket_size}", s.price_status)
    console.print(table)


@app.command("inspect-game")
def inspect_game(game_id: str) -> None:
    """Mostra a configuracao de um jogo."""
    _notice()
    s = registry.get(game_id)
    t = Table(title=f"{s.name} ({s.game_id})")
    t.add_column("campo")
    t.add_column("valor")
    rows = [("universo", f"{s.universe_min}-{s.universe_max} (N={s.pool})"),
            ("draw_size (K)", str(s.draw_size)),
            ("tamanhos de aposta", str(s.allowed_ticket_sizes)),
            ("faixas de premio", str(s.prize_tiers)),
            ("C(N,K)", f"{s.total_outcomes():,}"),
            ("config de preco", price_config_summary(s)),
            ("notas", s.notes or "-")]
    for k, v in rows:
        t.add_row(k, v)
    console.print(t)


@app.command("validate-config")
def validate_config(game_id: str) -> None:
    """Valida a configuracao do jogo."""
    _notice()
    from ..core.game import GameSpec

    try:
        s = registry.get(game_id)
        GameSpec(**s.model_dump())  # revalida
        console.print(f"[green]OK[/green] '{game_id}' valido.")
    except Exception as e:  # noqa: BLE001
        console.print(f"[red]INVALIDO:[/red] {e}")
        raise typer.Exit(code=2) from None


@app.command()
def generate(
    game: str, budget: int = 10, strategy: str = "hybrid_initial", seed: int = 12345,
    ticket_size: int = 0, mixed_ticket_sizes: str = "", output_dir: str = "",
    allow_example_prices: bool = False,
) -> None:
    """Gera uma carteira inicial e exporta tudo."""
    _notice()
    spec = registry.get(game)
    _check_real_run(spec, allow_example_prices)
    gen = GENERATORS.get(strategy)
    if gen is None:
        console.print(f"[red]Estrategia desconhecida:[/red] {strategy} (use {list(GENERATORS)})")
        raise typer.Exit(code=2)
    constraints = _constraints(ticket_size, mixed_ticket_sizes or None)
    portfolio = gen().generate(spec, budget, constraints, seed)
    run_dir = _run_dir(output_dir, game)
    _export_all(portfolio, spec, run_dir, algorithm=f"gen:{strategy}", seed=seed,
                params={"strategy": strategy, "budget": budget})
    console.print(f"[green]Gerada[/green] carteira de {len(portfolio)} apostas em {run_dir}")


@app.command()
def optimize(
    game: str, budget: int = 10, optimizer: str = "hybrid", runtime_seconds: float = 0.0,
    iterations: int = 200, seed: int = 12345, score_config: str = "", ticket_size: int = 0,
    mixed_ticket_sizes: str = "", output_dir: str = "", checkpoint: str = "", resume: str = "",
    allow_example_prices: bool = False,
) -> None:
    """Gera carteira inicial e otimiza."""
    _notice()
    spec = registry.get(game)
    _check_real_run(spec, allow_example_prices)
    if optimizer not in OPTIMIZERS:
        console.print(f"[red]Otimizador desconhecido:[/red] {optimizer} (use {list(OPTIMIZERS)})")
        raise typer.Exit(code=2)
    constraints = _constraints(ticket_size, mixed_ticket_sizes or None)
    initial = GENERATORS["hybrid_initial"]().generate(spec, budget, constraints, seed)
    sc = PortfolioScore.from_file(score_config) if score_config else None
    rc = RuntimeConfig(max_iterations=iterations,
                       runtime_seconds=runtime_seconds or None,
                       checkpoint_path=checkpoint or None)
    res = OPTIMIZERS[optimizer]().optimize(initial, spec, budget, sc, rc, seed)
    run_dir = _run_dir(output_dir, game)
    _export_all(res.best_portfolio, spec, run_dir, algorithm=optimizer, seed=seed,
                score_history=res.score_history,
                params={"optimizer": optimizer, "iterations": res.iterations,
                        "improvement": round(res.improvement, 6)})
    console.print(f"[green]Otimizada[/green] score {res.initial_score:.4f} -> {res.best_score:.4f} "
                  f"(+{res.improvement:.4f}) em {run_dir}")


@app.command()
def report(game: str, csv_path: str) -> None:
    """Relatorio TXT de uma carteira existente (jogos.csv)."""
    _notice()
    spec = registry.get(game)
    portfolio = load_csv(spec, csv_path)
    console.print(build_report(portfolio, spec))


@app.command()
def export(game: str, csv_path: str, output_dir: str = "") -> None:
    """Exporta CSV/Excel/TXT/graficos de uma carteira existente."""
    _notice()
    spec = registry.get(game)
    portfolio = load_csv(spec, csv_path)
    run_dir = _run_dir(output_dir, game)
    _export_all(portfolio, spec, run_dir, algorithm="export", seed=None)
    console.print(f"[green]Exportado[/green] para {run_dir}")


@app.command()
def compare(game: str, csv_a: str, csv_b: str) -> None:
    """Compara duas carteiras pelo score e cobertura."""
    _notice()
    spec = registry.get(game)
    pa, pb = load_csv(spec, csv_a), load_csv(spec, csv_b)
    ps = PortfolioScore()
    t = Table(title="Comparacao")
    for c in ("carteira", "apostas", "score", "cobertura_pares_unica"):
        t.add_column(c)
    from ..metrics.coverage import CoverageMetrics
    cov = CoverageMetrics(spec)
    for label, p in (("A", pa), ("B", pb)):
        t.add_row(label, str(len(p)), f"{ps.score(p, spec):.4f}", str(cov.pairs(p).unique))
    console.print(t)
    winner = "A" if ps.score(pa, spec) >= ps.score(pb, spec) else "B"
    console.print(f"[green]Melhor score:[/green] carteira {winner}")


@app.command()
def benchmark(
    game: str, budget: int = 8, seeds: str = "1", runtime_seconds: float = 0.0,
    iterations: int = 60, algorithms: str = "random,local_search,hybrid", output_dir: str = "",
    allow_example_prices: bool = False,
) -> None:
    """Compara algoritmos com a mesma seed, orcamento e GameSpec."""
    _notice()
    from ..benchmark import run_benchmark

    spec = registry.get(game)
    _check_real_run(spec, allow_example_prices)
    seed_list = [int(s) for s in seeds.split(",")]
    algos = [a.strip() for a in algorithms.split(",")]
    run_dir = _run_dir(output_dir, game)
    summary = run_benchmark(spec, budget, seed_list, algos, iterations, runtime_seconds or None, run_dir)
    t = Table(title="Benchmark")
    for c in ("algoritmo", "score", "melhoria", "cobertura_pares", "tempo_s", "valido"):
        t.add_column(c)
    for row in summary["rows"]:
        t.add_row(row["algorithm"], f"{row['score']:.4f}", f"{row['improvement']:.4f}",
                  str(row["pair_unique"]), f"{row['elapsed']:.2f}", "sim" if row["valid"] else "NAO")
    console.print(t)
    console.print(f"[green]Vencedor:[/green] {summary['winner']} -> arquivos em {run_dir}")


def main() -> None:  # pragma: no cover
    app()


if __name__ == "__main__":  # pragma: no cover
    app()
