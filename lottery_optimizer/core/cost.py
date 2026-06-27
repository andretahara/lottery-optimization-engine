"""CostModel: custo de apostas/carteiras. Precos oficiais nunca inventados (ADR-006).

Sem entrada oficial na price_table para um tamanho, o custo PODE ser estimado por
``base * C(T, K)`` e e SEMPRE marcado como estimativa (is_estimate=True).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .combinations import n_choose_k
from .game import GameSpec
from .portfolio import Portfolio
from .validation import SpecError


@dataclass(frozen=True)
class CostResult:
    amount: Decimal
    is_estimate: bool


class CostModel:
    """Calcula custo por aposta, total, saldo e custo por combinacao simples equivalente."""

    def __init__(self, spec: GameSpec, base_cost: Decimal | None = None):
        self.spec = spec
        # base do jogo simples: argumento explicito tem prioridade; senao preco oficial do
        # tamanho == draw_size, se houver. base nunca e inventada.
        self._base = base_cost
        if self._base is None and spec.price_table:
            self._base = spec.price_table.get(spec.draw_size)

    def ticket_cost(self, ticket_size: int) -> CostResult:
        """Custo de uma aposta de `ticket_size` dezenas (oficial se na tabela, senao estimativa)."""
        if ticket_size not in self.spec.allowed_ticket_sizes:
            raise SpecError(f"tamanho {ticket_size} nao permitido ({self.spec.allowed_ticket_sizes})")
        table = self.spec.price_table
        if table is not None and ticket_size in table:
            return CostResult(amount=table[ticket_size], is_estimate=False)
        if self._base is not None:
            est = self._base * n_choose_k(ticket_size, self.spec.draw_size)
            return CostResult(amount=Decimal(est), is_estimate=True)
        raise SpecError(
            f"sem preco oficial nem base para {ticket_size} marcas em '{self.spec.game_id}'; "
            "configure price_table ou base_cost (ADR-006)"
        )

    def portfolio_cost(self, portfolio: Portfolio) -> CostResult:
        """Custo total da carteira. is_estimate=True se qualquer aposta foi estimada."""
        total = Decimal("0")
        estimated = False
        for size in portfolio.ticket_sizes():
            r = self.ticket_cost(size)
            total += r.amount
            estimated = estimated or r.is_estimate
        return CostResult(amount=total, is_estimate=estimated)

    def balance(self, portfolio: Portfolio, budget: Decimal) -> CostResult:
        """Saldo = orcamento - custo total. is_estimate propaga do custo."""
        cost = self.portfolio_cost(portfolio)
        return CostResult(amount=budget - cost.amount, is_estimate=cost.is_estimate)

    def equivalent_simple_combinations(self, ticket_size: int) -> int:
        """C(T, K): jogos simples equivalentes a uma aposta de `ticket_size` dezenas."""
        return n_choose_k(ticket_size, self.spec.draw_size)

    def cost_per_simple_combination(self, ticket_size: int) -> CostResult:
        """Custo dividido pelas combinacoes simples equivalentes (eficiencia da aposta)."""
        r = self.ticket_cost(ticket_size)
        eq = self.equivalent_simple_combinations(ticket_size)
        return CostResult(amount=r.amount / eq, is_estimate=r.is_estimate)
