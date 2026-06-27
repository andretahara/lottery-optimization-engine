"""Interface comum dos geradores de carteira inicial.

Orcamento aqui = numero de apostas (contagem). Orcamento monetario exige precos oficiais
(bloqueado por padrao, ADR-020) e e resolvido fora do gerador. Estrategias de tamanho:
- all_simple: toda aposta no menor tamanho permitido (aposta simples).
- fixed: todas no tamanho `ticket_size`.
- mixed_ticket_sizes: alterna entre `mixed_sizes` (ou allowed_ticket_sizes).

Apostas multiplas (size > draw_size) NAO aumentam eficiencia matematica do premio principal
quando o custo por combinacao simples equivalente e igual: apenas consolidam combinacoes. A
engine as suporta por utilidade operacional e cobertura de faixas secundarias (docs/MATH_MODEL §5).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..core.game import GameSpec
from ..core.portfolio import Portfolio
from ..core.validation import SpecError
from ..utils.logging import get_logger
from ..utils.random import SeededRng

_log = get_logger("lottery_optimizer.generators")


@dataclass(frozen=True)
class GenerationConstraints:
    strategy: str = "all_simple"          # all_simple | fixed | mixed_ticket_sizes
    ticket_size: int | None = None        # usado em strategy=fixed
    mixed_sizes: tuple[int, ...] | None = None
    allow_duplicates: bool = False


class BaseGenerator(ABC):
    name: str = "generator"

    def generate(
        self, game_spec: GameSpec, budget: int, constraints: GenerationConstraints, seed: int
    ) -> Portfolio:
        """Gera uma carteira de `budget` apostas. Reprodutivel por seed, sem duplicatas."""
        if budget < 1:
            raise SpecError("budget (numero de apostas) deve ser >= 1")
        sizes = self._resolve_sizes(game_spec, budget, constraints)
        rng = SeededRng(seed)
        portfolio = self._build(game_spec, sizes, constraints, rng)
        _log.info(
            "%s gerou %d apostas (%s, seed=%d)", self.name, len(portfolio),
            constraints.strategy, seed,
        )
        return portfolio

    def _resolve_sizes(
        self, spec: GameSpec, budget: int, constraints: GenerationConstraints
    ) -> list[int]:
        if constraints.strategy == "fixed":
            size = constraints.ticket_size or spec.min_ticket_size
            sizes = [size] * budget
        elif constraints.strategy == "mixed_ticket_sizes":
            pool = constraints.mixed_sizes or spec.allowed_ticket_sizes
            sizes = [pool[i % len(pool)] for i in range(budget)]
        else:  # all_simple
            sizes = [spec.min_ticket_size] * budget
        for s in sizes:
            if s not in spec.allowed_ticket_sizes:
                raise SpecError(f"ticket size {s} nao permitido ({spec.allowed_ticket_sizes})")
        return sizes

    @abstractmethod
    def _build(
        self, spec: GameSpec, sizes: list[int], constraints: GenerationConstraints, rng: SeededRng
    ) -> Portfolio:
        ...

    # util comum: amostra um jogo unico que ainda nao esta em `seen`
    @staticmethod
    def _sample_unique(spec, size, rng, seen, max_tries=200):
        universe = list(spec.number_universe())
        for _ in range(max_tries):
            pick = tuple(sorted(rng.sample(universe, size)))
            if pick not in seen:
                return pick
        return None
