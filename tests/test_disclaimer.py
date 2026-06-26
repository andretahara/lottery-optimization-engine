from lottery_engine.disclaimer import DISCLAIMER


def test_disclaimer_exact_text():
    assert DISCLAIMER == (
        "Esta otimização não prevê números sorteados. Ela apenas maximiza cobertura "
        "e reduz redundância. Todas as combinações possíveis continuam tendo a mesma "
        "probabilidade individual."
    )


def test_disclaimer_key_phrase_present():
    assert "mesma probabilidade individual" in DISCLAIMER
    assert "não prevê" in DISCLAIMER
