"""GameRegistry: carrega/valida/lista jogos, aplica overrides de preco e jogos customizados.

A engine nao depende de internet e e reproduzivel. Precos sao responsabilidade do usuario
(ADR-006/020); overrides locais entram por arquivo YAML, nunca por rede.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from ..core.game import GameSpec

_CONFIG_DIR = Path(__file__).parent / "configs"
# arquivos que NAO sao spec de jogo (exemplos/overrides do usuario)
_NON_GAME = {"user_overrides.example.yaml"}


class GameRegistry:
    """Catalogo de jogos. Instancias sao isoladas (sem estado global mutavel)."""

    def __init__(self, config_dir: Path | str = _CONFIG_DIR):
        self._dir = Path(config_dir)
        self._specs: dict[str, GameSpec] = {}
        self._load_dir()

    def _load_dir(self) -> None:
        for path in sorted(self._dir.glob("*.yaml")):
            if path.name in _NON_GAME:
                continue
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            spec = GameSpec(**data)  # valida via pydantic; YAML invalido levanta
            if spec.game_id in self._specs:
                raise ValueError(f"game_id duplicado '{spec.game_id}' em {path.name}")
            self._specs[spec.game_id] = spec

    # --- consulta ---
    def available(self) -> tuple[str, ...]:
        return tuple(sorted(self._specs))

    def get(self, game_id: str) -> GameSpec:
        try:
            return self._specs[game_id]
        except KeyError:
            raise KeyError(
                f"loteria '{game_id}' desconhecida; disponiveis: {', '.join(self.available())}"
            ) from None

    # --- customizacao / overrides (retornam novo registry, sem mutar global) ---
    def add_custom(self, spec: GameSpec) -> None:
        """Registra um jogo customizado nesta instancia."""
        if spec.game_id in self._specs:
            raise ValueError(f"game_id '{spec.game_id}' ja existe")
        self._specs[spec.game_id] = spec

    def apply_overrides(self, overrides: dict[str, dict[str, Any]]) -> None:
        """Sobrescreve campos (tipicamente preco) de jogos existentes, revalidando."""
        for game_id, fields in overrides.items():
            if game_id not in self._specs:
                raise KeyError(f"override para jogo desconhecido '{game_id}'")
            base = self._specs[game_id].model_dump()
            base.update(fields)
            self._specs[game_id] = GameSpec(**base)  # revalida coerencia preco<->status

    def load_overrides_file(self, path: Path | str) -> None:
        """Aplica overrides de um YAML local (ex.: precos oficiais do usuario)."""
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        self.apply_overrides(data)


@lru_cache(maxsize=1)
def _default() -> GameRegistry:
    return GameRegistry()


def available() -> tuple[str, ...]:
    return _default().available()


def get(game_id: str) -> GameSpec:
    return _default().get(game_id)
