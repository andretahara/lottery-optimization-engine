# ARCHITECTURE - Lottery Optimization Engine

> **Atualizado (ADR-013):** o pacote real e `lottery_optimizer/` (layout flat na raiz),
> nao `src/lottery_engine`. Arvore vigente:
>
> ```
> lottery_optimizer/
>   __init__.py  disclaimer.py
>   core/      combinations.py game.py ticket.py portfolio.py probability.py cost.py validation.py
>   metrics/   frequency.py coverage.py distance.py balance.py scoring.py
>   algorithms/ base.py random_balanced.py local_search.py simulated_annealing.py genetic.py grasp.py  (stubs)
>   games/     registry.py  configs/*.yaml (6 loterias)
>   export/    csv_exporter.py report_exporter.py excel_exporter.py(stub) charts.py(stub)
>   cli/       main.py (typer)
>   utils/     random.py logging.py checkpoint.py
> tests/  scripts/  Makefile  pyproject.toml  requirements.txt
> ```
>
> Os principios abaixo (camadas sem ciclo, puro por default, config-nao-codigo,
> determinismo, falha explicita) seguem valendo, agora mapeados nesses modulos.

---


Nucleo de funcoes puras importavel + CLI fino. Loteria como configuracao. Modulos com
responsabilidade unica e dependencias explicitas. Sem rede, sem I/O implicito.

## 1. Layout

```
lottery-optimization-engine/
  pyproject.toml            # build PEP 621, deps, config ruff/pytest
  README.md
  CLAUDE.md
  docs/                     # SPEC, ARCHITECTURE, MATH_MODEL, ROADMAP, DECISIONS, TESTING
  src/lottery_engine/
    __init__.py             # exporta API publica estavel
    disclaimer.py           # DISCLAIMER: str (constante unica)
    spec.py                 # LotterySpec (dataclass) + validacao
    registry.py             # presets das loterias (precos None) + lookup por nome
    rng.py                  # wrapper de RNG com seed; uniformidade testavel
    combinatorics.py        # helpers: C(n,k), iteracao de combinacoes, subconjuntos
    generate.py             # geracao de jogos/carteira justa sob orcamento
    wheels.py               # covering designs / wheeling com garantia verificavel
    metrics.py              # avaliacao intra-carteira
    portfolio.py            # otimizacao de carteira (greedy + busca local)
    export.py               # CSV / Excel / relatorio (injeta disclaimer)
    cli.py                  # CLI fino (argparse)
  tests/                    # pytest (ver docs/TESTING.md)
```

## 2. Camadas e fluxo de dependencia

```
disclaimer        (folha, sem deps)
combinatorics     (stdlib)
spec  ->  (combinatorics)
registry  ->  spec
rng       (stdlib random/numpy)
generate  ->  spec, rng, combinatorics
wheels    ->  spec, combinatorics
metrics   ->  spec, combinatorics
portfolio ->  spec, metrics, generate, rng
export    ->  spec, metrics, disclaimer
cli       ->  registry, generate, wheels, portfolio, metrics, export
```

Regra: setas so para baixo/lateral; sem ciclos. `cli` e o unico orquestrador; nucleo nao
depende de `cli`. Nada importa `export` exceto `cli` (e testes).

## 3. Responsabilidade de cada modulo

- **disclaimer**: a string exata do aviso. Importada por export e cli. Fonte unica.
- **combinatorics**: `n_choose_k`, geracao/contagem de combinacoes e k-subconjuntos. Puro.
- **spec**: `LotterySpec` dataclass imutavel + `validate()`. Sem logica de geracao.
- **registry**: dict nome->factory de spec para as 8 loterias; precos `None`. `get(name)`.
- **rng**: `Rng(seed)` determinista; amostragem uniforme de combinacoes sem vies.
- **generate**: carteira aleatoria justa, respeitando `min/max_marks` e orcamento (contagem
  de jogos; ou valor se `price_table` setado). Sem duplicatas por default.
- **wheels**: dado conjunto de M dezenas + garantia desejada (K', J), retorna jogos abreviados
  que satisfazem a garantia; expoe verificador de garantia.
- **metrics**: funcoes puras carteira->numeros: cobertura de pares/trincas, matriz de
  sobreposicao, balanco de frequencia das dezenas, distancia media par-a-par, indice de redundancia.
- **portfolio**: dado orcamento e spec, constroi/melhora carteira maximizando cobertura e
  diversidade, minimizando sobreposicao/redundancia. Usa metrics como funcao-objetivo.
- **export**: serializa carteira+metricas para CSV, Excel (openpyxl), relatorio txt/md.
  SEMPRE injeta `DISCLAIMER`.
- **cli**: parse de args (loteria, orcamento, modo, seed, saida), chama nucleo, exporta.

## 4. Contratos de dados (formas, nao implementacao)

- `Ticket = tuple[int, ...]` (T dezenas ordenadas, distintas).
- `Portfolio = list[Ticket]` (sem duplicatas por default).
- `LotterySpec`: ver `docs/SPEC.md` secao 4.
- `Metrics`: dataclass/dict com chaves estaveis (`pair_coverage`, `triple_coverage`,
  `mean_overlap`, `digit_balance`, `mean_distance`, `redundancy`).

## 5. Principios

- **Puro por default**: nucleo sem efeitos colaterais; I/O so em export/cli.
- **Determinismo**: toda aleatoriedade passa por `rng` com seed -> testes reproduziveis.
- **Configuracao, nao codigo**: nova loteria = nova spec no registry, zero ramificacao por nome.
- **Falha explicita**: preco ausente em orcamento monetario levanta erro claro, nao chuta.
- **Sem dependencia oculta de rede/relogio**.

## 6. Dependencias externas

- Nucleo: stdlib (`itertools`, `random`, `math`, `dataclasses`, `decimal`). `numpy` opcional p/ metrics.
- Export Excel: `openpyxl`.
- Dev: `pytest`, `hypothesis`, `ruff`.

Decisoes registradas em `docs/DECISIONS.md`.
