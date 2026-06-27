"""Checkpoints JSON simples para retomada (CLAUDE.md §11-12)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def save_checkpoint(data: dict[str, Any], path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def load_checkpoint(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
