"""Ticket: um jogo (conjunto de dezenas distintas)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, field_validator

from .validation import TicketError


class Ticket(BaseModel):
    """Jogo imutavel: dezenas distintas, armazenadas ordenadas."""

    model_config = ConfigDict(frozen=True)

    numbers: tuple[int, ...]

    @field_validator("numbers", mode="before")
    @classmethod
    def _normalize(cls, v: object) -> tuple[int, ...]:
        nums = tuple(v)  # type: ignore[arg-type]
        if len(set(nums)) != len(nums):
            raise TicketError(f"dezenas repetidas: {nums}")
        if not nums:
            raise TicketError("ticket vazio")
        return tuple(sorted(nums))

    def __len__(self) -> int:
        return len(self.numbers)

    def matches(self, draw: "Ticket | tuple[int, ...]") -> int:
        """Quantidade de dezenas em comum com um sorteio."""
        other = draw.numbers if isinstance(draw, Ticket) else tuple(draw)
        return len(set(self.numbers) & set(other))

    def overlap(self, other: "Ticket") -> int:
        """Dezenas em comum com outro jogo (redundancia)."""
        return len(set(self.numbers) & set(other.numbers))
