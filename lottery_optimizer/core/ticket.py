"""Ticket: uma aposta (dezenas distintas em ordem canonica), validavel contra a GameSpec."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, field_validator

from .validation import TicketError


class Ticket(BaseModel):
    """Jogo imutavel: dezenas distintas armazenadas ordenadas (ordem canonica)."""

    model_config = ConfigDict(frozen=True)

    numbers: tuple[int, ...]

    @field_validator("numbers", mode="before")
    @classmethod
    def _normalize(cls, v: object) -> tuple[int, ...]:
        nums = tuple(v)  # type: ignore[arg-type]
        if not nums:
            raise TicketError("ticket vazio")
        if len(set(nums)) != len(nums):
            raise TicketError(f"dezenas repetidas: {nums}")
        return tuple(sorted(nums))

    def __len__(self) -> int:
        return len(self.numbers)

    def matches(self, draw: "Ticket | tuple[int, ...]") -> int:
        other = draw.numbers if isinstance(draw, Ticket) else tuple(draw)
        return len(set(self.numbers) & set(other))

    def overlap(self, other: "Ticket") -> int:
        return len(set(self.numbers) & set(other.numbers))

    def validate_against(self, spec) -> None:
        """Levanta TicketError se o jogo for incompativel com a spec."""
        from .game import GameSpec  # evita import circular

        assert isinstance(spec, GameSpec)
        if len(self.numbers) not in spec.allowed_ticket_sizes:
            raise TicketError(
                f"tamanho {len(self.numbers)} nao permitido em '{spec.game_id}' "
                f"({spec.allowed_ticket_sizes})"
            )
        for n in self.numbers:
            if not spec.contains(n):
                raise TicketError(
                    f"dezena {n} fora do universo [{spec.universe_min}, {spec.universe_max}]"
                )

    @classmethod
    def create(cls, spec, numbers) -> "Ticket":
        """Cria um Ticket ja validado contra a spec."""
        t = cls(numbers=tuple(numbers))
        t.validate_against(spec)
        return t
