"""GameSpec: loteria como configuracao validada (ADR-003, ADR-014 pydantic)."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator

from .combinations import n_choose_k
from .validation import SpecError


class GameSpec(BaseModel):
    """Especificacao imutavel de uma loteria combinatoria.

    Universo: inteiros de ``number_start`` a ``number_start + pool - 1``. A aposta marca
    de ``min_marks`` a ``max_marks`` dezenas; o sorteio escolhe ``draw_size``.
    ``prize_tiers`` = quantidades de acerto que premiam (crescente). ``price_table`` = None
    ate o usuario configurar precos vigentes (ADR-006).
    """

    model_config = ConfigDict(frozen=True)

    slug: str
    name: str
    pool: int  # N
    draw_size: int  # K
    min_marks: int  # menor T
    max_marks: int  # maior T
    prize_tiers: tuple[int, ...]
    number_start: int = 1
    price_table: dict[int, Decimal] | None = None
    extra_rules: dict[str, Any] = {}

    @model_validator(mode="after")
    def _check(self) -> "GameSpec":
        if not self.name or not self.slug:
            raise SpecError("slug/name vazio")
        if self.pool <= 0:
            raise SpecError(f"pool deve ser > 0, recebido {self.pool}")
        if not (1 <= self.draw_size <= self.pool):
            raise SpecError(f"draw_size deve estar em [1, {self.pool}], recebido {self.draw_size}")
        if not (1 <= self.min_marks <= self.max_marks <= self.pool):
            raise SpecError(
                f"exige 1 <= min_marks <= max_marks <= pool; "
                f"min={self.min_marks} max={self.max_marks} pool={self.pool}"
            )
        if self.min_marks < self.draw_size:
            raise SpecError(
                f"min_marks ({self.min_marks}) < draw_size ({self.draw_size}): "
                "aposta precisa marcar ao menos o tamanho do sorteio"
            )
        if not self.prize_tiers:
            raise SpecError("prize_tiers vazio")
        if list(self.prize_tiers) != sorted(set(self.prize_tiers)):
            raise SpecError(f"prize_tiers deve ser crescente e sem repetidos: {self.prize_tiers}")
        max_hits = min(self.draw_size, self.max_marks)
        for tier in self.prize_tiers:
            if not (0 <= tier <= max_hits):
                raise SpecError(f"tier {tier} fora de [0, {max_hits}]")
        if self.price_table is not None:
            for marks in self.price_table:
                if not (self.min_marks <= marks <= self.max_marks):
                    raise SpecError(
                        f"price_table tem marcas {marks} fora de [{self.min_marks}, {self.max_marks}]"
                    )
        return self

    @property
    def number_end(self) -> int:
        return self.number_start + self.pool - 1

    def number_universe(self) -> range:
        return range(self.number_start, self.number_end + 1)

    def total_outcomes(self) -> int:
        """C(pool, draw_size): tamanho do espaco amostral."""
        return n_choose_k(self.pool, self.draw_size)

    def simple_combinations(self, marks: int) -> int:
        """C(marks, draw_size): jogos simples equivalentes a uma aposta de `marks` dezenas."""
        if not (self.min_marks <= marks <= self.max_marks):
            raise SpecError(f"marks {marks} fora de [{self.min_marks}, {self.max_marks}]")
        return n_choose_k(marks, self.draw_size)
