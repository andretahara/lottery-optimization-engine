"""GameSpec: loteria combinatoria como configuracao (ADR-003, ADR-014, ADR-017).

Nenhuma regra de loteria especifica mora nas funcoes do nucleo: tudo vem da GameSpec.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from .combinations import n_choose_k
from .validation import SpecError


class GameSpec(BaseModel):
    """Especificacao imutavel de uma loteria combinatoria.

    Universo: inteiros de ``universe_min`` a ``universe_max`` (inclusive). O sorteio escolhe
    ``draw_size`` dezenas. A aposta marca uma quantidade em ``allowed_ticket_sizes``.
    ``price_table`` mapeia tamanho->preco oficial (None ate o usuario configurar, ADR-006).
    ``prize_tiers`` e ``notes`` sao opcionais.
    """

    model_config = ConfigDict(frozen=True)

    game_id: str
    name: str
    universe_min: int
    universe_max: int
    draw_size: int  # K
    allowed_ticket_sizes: tuple[int, ...]
    price_table: dict[int, Decimal] | None = None
    prize_tiers: tuple[int, ...] | None = None
    notes: str | None = None

    @field_validator("allowed_ticket_sizes", mode="before")
    @classmethod
    def _norm_sizes(cls, v: Any) -> tuple[int, ...]:
        return tuple(sorted(set(v)))

    @field_validator("prize_tiers", mode="before")
    @classmethod
    def _norm_tiers(cls, v: Any) -> Any:
        if v is None:
            return None
        return tuple(sorted(set(v)))

    @model_validator(mode="after")
    def _check(self) -> "GameSpec":
        if not self.game_id or not self.name:
            raise SpecError("game_id/name vazio")
        if self.universe_min > self.universe_max:
            raise SpecError(
                f"universe_min ({self.universe_min}) > universe_max ({self.universe_max})"
            )
        pool = self.pool
        if not (1 <= self.draw_size <= pool):
            raise SpecError(f"draw_size deve estar em [1, {pool}], recebido {self.draw_size}")
        if not self.allowed_ticket_sizes:
            raise SpecError("allowed_ticket_sizes vazio")
        for size in self.allowed_ticket_sizes:
            if not (self.draw_size <= size <= pool):
                raise SpecError(
                    f"ticket size {size} fora de [draw_size={self.draw_size}, pool={pool}]"
                )
        if self.prize_tiers is not None:
            for tier in self.prize_tiers:
                if not (0 <= tier <= self.draw_size):
                    raise SpecError(f"prize tier {tier} fora de [0, draw_size={self.draw_size}]")
        if self.price_table is not None:
            for size in self.price_table:
                if size not in self.allowed_ticket_sizes:
                    raise SpecError(
                        f"price_table tem tamanho {size} fora de allowed_ticket_sizes"
                    )
        return self

    # --- derivados ---
    @property
    def pool(self) -> int:
        """N: quantidade de dezenas no universo."""
        return self.universe_max - self.universe_min + 1

    @property
    def min_ticket_size(self) -> int:
        return self.allowed_ticket_sizes[0]

    @property
    def max_ticket_size(self) -> int:
        return self.allowed_ticket_sizes[-1]

    def number_universe(self) -> range:
        return range(self.universe_min, self.universe_max + 1)

    def contains(self, number: int) -> bool:
        return self.universe_min <= number <= self.universe_max

    def total_outcomes(self) -> int:
        """C(N, K): tamanho do espaco amostral do sorteio."""
        return n_choose_k(self.pool, self.draw_size)

    def simple_combinations(self, ticket_size: int) -> int:
        """C(T, K): jogos simples equivalentes a uma aposta de `ticket_size` dezenas."""
        if ticket_size not in self.allowed_ticket_sizes:
            raise SpecError(f"ticket size {ticket_size} nao permitido ({self.allowed_ticket_sizes})")
        return n_choose_k(ticket_size, self.draw_size)
