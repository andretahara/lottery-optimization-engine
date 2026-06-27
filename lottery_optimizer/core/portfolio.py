"""Portfolio: carteira de jogos comprada de uma vez."""

from __future__ import annotations

from .ticket import Ticket
from .validation import TicketError


class Portfolio:
    """Colecao ordenada de jogos. Sem duplicatas por default."""

    def __init__(self, tickets: list[Ticket] | None = None, *, allow_duplicates: bool = False):
        self.allow_duplicates = allow_duplicates
        self._tickets: list[Ticket] = []
        for t in tickets or []:
            self.add(t)

    def add(self, ticket: Ticket) -> None:
        if not self.allow_duplicates and ticket in self._tickets:
            raise TicketError(f"jogo duplicado: {ticket.numbers}")
        self._tickets.append(ticket)

    @property
    def tickets(self) -> tuple[Ticket, ...]:
        return tuple(self._tickets)

    def __len__(self) -> int:
        return len(self._tickets)

    def __iter__(self):
        return iter(self._tickets)
