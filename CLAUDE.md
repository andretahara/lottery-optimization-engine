# CLAUDE.md - Lottery Optimization Engine (memoria operacional permanente)

Relido no inicio de TODA sessao (inclusive apos /clear ou crash). Curto e objetivo.
Ao retomar: reler tambem `docs/ROADMAP.md` e `docs/DECISIONS.md`, inspecionar a arvore
e o estado dos testes, continuar do ponto pendente. Nunca recomecar nem duplicar.

## 1. Comandos principais

```bash
python -m venv .venv && source .venv/bin/activate   # ambiente
pip install -e ".[dev]"                              # instalar (engine + dev tools)
pytest -q                                            # rodar todos os testes
pytest tests/test_<modulo>.py -q                     # rodar um modulo
ruff check src tests                                 # lint
ruff format src tests                                # format
python -m lottery_engine.cli --help                  # CLI
```
(Comandos validos a partir do Bloco 1, quando `pyproject.toml` e `src/` existem.)

## 2. Padrao de arquitetura

Nucleo de funcoes puras importavel + CLI fino. Layout `src/lottery_engine/`. Loteria e
SEMPRE configuracao (`LotterySpec`/registry), nunca hardcode/`if nome ==`. Modulos com
uma responsabilidade so. Detalhe em `docs/ARCHITECTURE.md`.

## 3. Padrao de testes

Tudo via `pytest`. Unitarios + propriedade (hypothesis) + integracao + export + repro.
Garantias combinatorias (wheeling) provadas por forca bruta em casos pequenos. RNG com
seed fixa para reprodutibilidade. Detalhe em `docs/TESTING.md`.

## 4. Regras matematicas (inviolaveis)

Todas as dezenas tem a MESMA probabilidade. PROIBIDO como sinal de selecao: quente, frio,
atrasado, ciclo, data, numerologia, padrao historico, supersticao. A engine otimiza SO
cobertura combinatoria e qualidade de carteira (diversidade, baixa sobreposicao, balanco
intra-carteira, distancia, orcamento). Fundamentacao em `docs/MATH_MODEL.md`.

## 5. NAO usar dados historicos de sorteios

Sorteios passados nao alimentam selecao (ADR-004). Sem fetcher de rede no nucleo (ADR-007).
Metricas sao sobre a CARTEIRA GERADA, nunca sobre o historico.

## 6. NAO hardcodar precos oficiais

`LotterySpec.price_table` = `None` placeholder. Usuario seta preco vigente antes de
orcamento monetario. Orcamento por contagem de jogos funciona sem preco. (ADR-006)

## 7. Validar tudo com pytest

Nenhuma feature considerada feita sem teste correspondente verde.

## 8. NAO encerrar tarefa sem rodar os testes relevantes

Antes de devolver controle: rodar pytest do escopo tocado e confirmar verde. "Pronto"
exige prova (saida dos testes), nao auto-afirmacao.

## 9. Atualizar docs/DECISIONS.md em decisao arquitetural

Toda escolha de arquitetura/ambiguidade resolvida vira ADR (contexto/decisao/consequencia).

## 10. PERSISTENCIA

Concluir o bloco atual por completo antes de devolver controle. Nao pedir permissao para
passos seguros (criar arquivos, instalar deps, rodar testes, corrigir falhas, refatorar
no escopo). So interromper em decisao irreversivel, ambigua de alto impacto, ou que dependa
de info externa indisponivel (ex.: preco oficial vigente).

## 11. RESILIENCIA

"API error", timeout, rate limit, queda de rede, processo morto = interrupcao TEMPORARIA,
nunca fim da tarefa. Retomar relendo CLAUDE.md + ROADMAP + DECISIONS e continuar do ponto
pendente. Retry com backoff em shell sujeito a falha transitoria (install/download).
Distinguir falha transitoria de bug real: bug se corrige, nao se "retrya".

## 12. CHECKPOINTS

`docs/ROADMAP.md` sempre marcado `[x]`/`[~]`/`[ ]`. Commit local descritivo ao concluir
cada unidade. Nunca deixar o projeto quebrado: parar so em ponto com testes verdes ou
estado documentado em DECISIONS.

## 13. AUTOCRITICA

Nao confiar em "esta pronto" sem testes verdes e fluxo demonstrado.

## Git

`git push` SO sob pedido explicito. Nunca `git add -A`/`.`; paths especificos; conferir
`git status --short` antes do commit.

## Aviso obrigatorio (constante unica em `disclaimer.py`)

> Esta otimizacao nao preve numeros sorteados. Ela apenas maximiza cobertura e reduz
> redundancia. Todas as combinacoes possiveis continuam tendo a mesma probabilidade individual.
