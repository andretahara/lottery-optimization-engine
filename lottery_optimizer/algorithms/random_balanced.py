"""Geracao justa de carteira.

Dois modos, ambos SEM previsao e SEM favorecer dezena alguma (equiprobabilidade intacta):
- balanced=False: cada jogo e uma combinacao uniformemente aleatoria do universo (amostragem justa).
- balanced=True : reduz a variancia da frequencia das dezenas DENTRO da carteira, de forma
  simetrica (todas as dezenas com mesma representacao esperada). Nao usa quente/frio/historico.
"""

from __future__ import annotations

from ..core.combinations import n_choose_k
from ..core.game import GameSpec
from ..core.portfolio import Portfolio
from ..core.ticket import Ticket
from ..core.validation import SpecError
from ..utils.random import SeededRng
from .base import Optimizer


class RandomBalancedOptimizer(Optimizer):
    name = "random-balanced"

    def __init__(self, balanced: bool = True):
        self.balanced = balanced

    def optimize(
        self, spec: GameSpec, num_tickets: int, marks: int, rng: SeededRng
    ) -> Portfolio:
        if marks not in spec.allowed_ticket_sizes:
            raise SpecError(f"marks {marks} nao permitido ({spec.allowed_ticket_sizes})")
        if num_tickets < 1:
            raise SpecError("num_tickets deve ser >= 1")
        max_distinct = n_choose_k(spec.pool, marks)
        if num_tickets > max_distinct:
            raise SpecError(
                f"num_tickets {num_tickets} excede combinacoes distintas C({spec.pool},{marks})="
                f"{max_distinct}"
            )

        universe = list(spec.number_universe())
        seen: set[tuple[int, ...]] = set()
        tickets: list[Ticket] = []
        counts = {n: 0 for n in universe}
        max_attempts = num_tickets * 50 + 100
        attempts = 0

        while len(tickets) < num_tickets and attempts < max_attempts:
            attempts += 1
            if self.balanced:
                # embaralha (desempate aleatorio entre dezenas de mesma contagem), depois
                # ordena de forma estavel pela contagem -> escolhe as MENOS usadas. Simetrico:
                # nenhuma dezena especifica e favorecida, so a representacao e equilibrada.
                order = rng.shuffle(universe)
                order.sort(key=lambda n: counts[n])
                pick = tuple(sorted(order[:marks]))
            else:
                pick = tuple(sorted(rng.sample(universe, marks)))
            if pick in seen:
                continue
            seen.add(pick)
            tickets.append(Ticket(numbers=pick))
            for n in pick:
                counts[n] += 1

        if len(tickets) < num_tickets:
            raise SpecError(
                f"nao foi possivel gerar {num_tickets} jogos distintos em {max_attempts} tentativas"
            )
        return Portfolio(spec, tickets)
