from lottery_optimizer.games import registry
from lottery_optimizer.utils.checkpoint import load_checkpoint, save_checkpoint
from lottery_optimizer.utils.random import SeededRng


def test_seeded_rng_deterministic():
    a = SeededRng(123).sample(range(1, 61), 6)
    b = SeededRng(123).sample(range(1, 61), 6)
    assert a == b


def test_different_seed_changes_output():
    a = SeededRng(1).sample(range(1, 61), 6)
    b = SeededRng(2).sample(range(1, 61), 6)
    assert a != b


def test_registry_specs_stable():
    assert registry.get("quina") == registry.get("quina")


def test_checkpoint_roundtrip(tmp_path):
    p = save_checkpoint({"bloco": 2, "ok": True}, tmp_path / "ck.json")
    assert load_checkpoint(p) == {"bloco": 2, "ok": True}
