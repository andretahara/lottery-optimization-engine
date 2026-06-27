"""CostModel: custo de apostas/carteiras. Precos oficiais nunca inventados (ADR-006/019/020).

`is_estimate=True` sempre que o valor NAO for um preco oficial: estimativa base*C(T,K),
ou preco de exemplo (price_status != 'official').
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
    def __init__(self, spec: GameSpec, base_cost: Decimal | None = None):
        self.spec = spec
        self._base = base_cost
        if self._base is None and spec.price_table:
            self._base = spec.price_table.get(spec.draw_size)

    def _official(self) -> bool:
        return self.spec.price_status == "official"

    def ticket_cost(self, ticket_size: int) -> CostResult:
        if ticket_size not in self.spec.allowed_ticket_sizes:
            raise SpecError(f"tamanho {ticket_size} nao permitido ({self.spec.allowed_ticket_sizes})")
        table = self.spec.price_table
        if table is not None and ticket_size in table:
            # preco tabelado: oficial so se a spec marca official; senao e exemplo (estimativa)
            return CostResult(amount=table[ticket_size], is_estimate=not self._official())
        if self._base is not None:
            est = self._base * n_choose_k(ticket_size, self.spec.draw_size)
            return CostResult(amount=Decimal(est), is_estimate=True)
        raise SpecError(
            f"sem preco oficial nem base para {ticket_size} marcas em '{self.spec.game_id}'; "
            "configure price_table ou base_cost (ADR-006)"
        )

    def portfolio_cost(self, portfolio: Portfolio) -> CostResult:
        total = Decimal("0")
        estimated = False
        for size in portfolio.ticket_sizes():
            r = self.ticket_cost(size)
            total += r.amount
            estimated = estimated or r.is_estimate
        return CostResult(amount=total, is_estimate=estimated)

    def balance(self, portfolio: Portfolio, budget: Decimal) -> CostResult:
        cost = self.portfolio_cost(portfolio)
        return CostResult(amount=budget - cost.amount, is_estimate=cost.is_estimate)

    def equivalent_simple_combinations(self, ticket_size: int) -> int:
        return n_choose_k(ticket_size, self.spec.draw_size)

    def cost_per_simple_combination(self, ticket_size: int) -> CostResult:
        r = self.ticket_cost(ticket_size)
        eq = self.equivalent_simple_combinations(ticket_size)
        return CostResult(amount=r.amount / eq, is_estimate=r.is_estimate)
