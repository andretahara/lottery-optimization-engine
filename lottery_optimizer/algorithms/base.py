"""Interface dos otimizadores de carteira + resultado + movimentos de vizinhanca.

Otimizar = melhorar uma carteira inicial mantendo: orcamento (numero de apostas) fixo, sem
duplicatas, dezenas no universo, tamanhos permitidos. Score via PortfolioScore (criterio
principal = cobertura UNICA de K-subsets). Reprodutivel por seed.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable

from ..core.game import GameSpec
from ..core.portfolio import Portfolio
from ..core.ticket import Ticket
from ..metrics.scoring import PortfolioScore
from ..utils.random import SeededRng


@dataclass
class RuntimeConfig:
    max_iterations: int = 500
    runtime_seconds: float | None = None
    restarts: int = 3
    checkpoint_path: str | None = None
    checkpoint_every: int = 100
    coverage_mode: str = "auto"
    max_memory_mode: str = "normal"  # normal | conservative
    # genetic
    population: int = 20
    generations: int = 40
    mutation_rate: float = 0.3
    elite: int = 2
    # SA
    temp_initial: float = 1.0
    cooling: float = 0.95
    # GRASP
    grasp_rounds: int = 5


@dataclass
class OptimizationResult:
    best_portfolio: Portfolio
    best_score: float
    initial_score: float
    improvement: float
    iterations: int
    elapsed_seconds: float
    score_history: list[float] = field(default_factory=list)
    accepted_moves: int = 0
    rejected_moves: int = 0
    checkpoint_path: str | None = None
    logs: list[str] = field(default_factory=list)


def make_scorer(score_config, spec: GameSpec, coverage_mode: str,
                max_memory_mode: str = "normal") -> Callable[[Portfolio], float]:
    """Normaliza score_config (PortfolioScore | dict | None) numa funcao carteira->float.

    Memoiza por assinatura da carteira: otimizadores reavaliam a mesma carteira varias vezes
    (ex.: replace-worst) - o cache evita recomputar a cobertura (caro). Nao altera resultado.
    """
    if isinstance(score_config, PortfolioScore):
        ps = score_config
    elif isinstance(score_config, dict):
        ps = PortfolioScore(weights=score_config.get("weights", score_config),
                            penalties=score_config.get("penalties"), max_memory_mode=max_memory_mode)
    else:
        ps = PortfolioScore(max_memory_mode=max_memory_mode)
    cache: dict = {}

    def scorer(p: Portfolio) -> float:
        key = frozenset(t.numbers for t in p)
        if key not in cache:
            cache[key] = ps.score(p, spec, coverage_mode=coverage_mode)
        return cache[key]

    return scorer


# ---------- movimentos de vizinhanca (preservam orcamento e validade) ----------

def _copy(spec, tickets) -> Portfolio:
    return Portfolio(spec, list(tickets))


def neighbor_swap_number(spec: GameSpec, portfolio: Portfolio, rng: SeededRng) -> Portfolio | None:
    """Troca UMA dezena de UMA aposta por outra do universo (mantem tamanho, sem duplicar jogo)."""
    tickets = list(portfolio)
    i = rng.randint(0, len(tickets) - 1)
    nums = list(tickets[i].numbers)
    universe = [n for n in spec.number_universe() if n not in nums]
    if not universe:
        return None
    pos = rng.randint(0, len(nums) - 1)
    nums[pos] = rng.sample(universe, 1)[0]
    new_t = Ticket(numbers=tuple(sorted(nums)))
    others = {t.numbers for j, t in enumerate(tickets) if j != i}
    if new_t.numbers in others:
        return None
    tickets[i] = new_t
    return _copy(spec, tickets)


def neighbor_swap_ticket(spec: GameSpec, portfolio: Portfolio, rng: SeededRng) -> Portfolio | None:
    """Substitui UMA aposta inteira por um jogo novo aleatorio do mesmo tamanho (sem duplicar)."""
    tickets = list(portfolio)
    i = rng.randint(0, len(tickets) - 1)
    size = len(tickets[i])
    universe = list(spec.number_universe())
    others = {t.numbers for j, t in enumerate(tickets) if j != i}
    for _ in range(50):
        cand = tuple(sorted(rng.sample(universe, size)))
        if cand not in others:
            tickets[i] = Ticket(numbers=cand)
            return _copy(spec, tickets)
    return None


def neighbor_replace_worst(
    spec: GameSpec, portfolio: Portfolio, rng: SeededRng, scorer: Callable[[Portfolio], float]
) -> Portfolio | None:
    """Remove a aposta cuja ausencia menos piora o score e tenta uma melhor no lugar."""
    tickets = list(portfolio)
    if len(tickets) < 2:
        return neighbor_swap_ticket(spec, portfolio, rng)
    # aposta "pior" = a que, removida, deixa o maior score residual
    worst_i, best_residual = 0, float("-inf")
    for i in range(len(tickets)):
        residual = scorer(_copy(spec, tickets[:i] + tickets[i + 1:]))
        if residual > best_residual:
            best_residual, worst_i = residual, i
    base = tickets[:worst_i] + tickets[worst_i + 1:]
    size = len(tickets[worst_i])
    universe = list(spec.number_universe())
    others = {t.numbers for t in base}
    best_p, best_s = None, float("-inf")
    for _ in range(30):
        cand = tuple(sorted(rng.sample(universe, size)))
        if cand in others:
            continue
        trial = _copy(spec, base + [Ticket(numbers=cand)])
        s = scorer(trial)
        if s > best_s:
            best_s, best_p = s, trial
    return best_p


_MOVES = [neighbor_swap_number, neighbor_swap_ticket]


def random_neighbor(spec, portfolio, rng, scorer=None) -> Portfolio | None:
    """Aplica um movimento aleatorio (troca de dezena ou de aposta)."""
    move = _MOVES[rng.randint(0, len(_MOVES) - 1)]
    return move(spec, portfolio, rng)


class BaseOptimizer(ABC):
    name: str = "optimizer"

    @abstractmethod
    def optimize(
        self, initial_portfolio: Portfolio, game_spec: GameSpec, budget: int,
        score_config, runtime_config: RuntimeConfig, seed: int,
    ) -> OptimizationResult:
        ...

    # util comum: cronometro e checkpoint
    @staticmethod
    def _now() -> float:
        return time.perf_counter()
