# Lottery Optimization Engine

[![CI](https://github.com/andretahara/lottery-optimization-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/andretahara/lottery-optimization-engine/actions/workflows/ci.yml) ![coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/andretahara/lottery-optimization-engine/badges/coverage.json)

Engine generica para loterias combinatorias brasileiras. Otimiza **cobertura
combinatoria** e **qualidade de carteira** (diversidade, baixa sobreposicao, balanco,
distancia media, aderencia ao orcamento). Trata cada loteria como configuracao, nunca
hardcode.

> Esta otimizacao nao preve numeros sorteados. Ela apenas maximiza cobertura e reduz
> redundancia. Todas as combinacoes possiveis continuam tendo a mesma probabilidade
> individual.

## O que NAO e

Nao e preditor. Nao usa numeros quentes/frios/atrasados, datas, numerologia, ciclos ou
padroes historicos. Loteria justa = toda combinacao tem a mesma probabilidade. Ver a
regra fundamental em `CLAUDE.md` e os ADRs em `docs/DECISIONS.md`.

## Loterias-alvo

Quina, Quina de Sao Joao, Mega-Sena, Mega-Sena da Virada, Lotofacil, Lotomania,
Timemania, Dupla Sena, e outras configuraveis.

## Usage

Instalacao (modo editavel, a partir do clone):

```bash
git clone https://github.com/andretahara/lottery-optimization-engine.git
cd lottery-optimization-engine
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

O executavel e `lottery-optimizer` (entrypoint declarado no `pyproject.toml`).
Todos os comandos abaixo foram executados de verdade; os trechos de saida sao reais
(recortados).

```bash
# Lista todos os comandos disponiveis
lottery-optimizer --help
```

```bash
# Lista as loterias configuradas (repare na coluna "preco": unset vs official)
lottery-optimizer list-games
```

```text
│ mega-sena  │ Mega-Sena  │ 1-60     │ 6       │ 6-15     │ unset    │
│ quina      │ Quina      │ 1-80     │ 5       │ 5-15     │ official │
```

```bash
# Mostra a config de um jogo (universo, K, C(N,K), status de preco)
lottery-optimizer inspect-game mega-sena
```

```bash
# Valida a config de um jogo
lottery-optimizer validate-config quina
# -> OK 'quina' valido.
```

```bash
# Gera uma carteira. budget = NUMERO DE APOSTAS. mega-sena nao tem preco oficial
# (price_status=unset), entao roda em modo CONTAGEM: sem custo monetario, sem aposta
# real. Artefatos (CSV/Excel/TXT/PNG) vao para output/ (gitignored).
lottery-optimizer generate mega-sena --budget 5 --seed 42 --output-dir output/exemplo
# -> Gerada carteira de 5 apostas em output/exemplo/<timestamp>_mega-sena
```

```bash
# Otimiza a carteira (refina cobertura/score; nunca piora o inicial)
lottery-optimizer optimize mega-sena --budget 5 --seed 42 --iterations 50 --output-dir output/exemplo_opt
# -> Otimizada score 0.2216 -> 0.2545 (+0.0329) em output/exemplo_opt/<timestamp>_mega-sena
```

```bash
# Relatorio TXT de uma carteira existente (ordem dos argumentos: GAME depois CSV)
lottery-optimizer report mega-sena output/exemplo/<timestamp>_mega-sena/jogos.csv
```

```text
Apostas: 5    Tamanhos: [6]
Combinacoes simples equivalentes: 5
```

**Precos e a flag `--allow-example-prices`.** A engine NAO preve sorteios: maximiza
cobertura combinatoria e reduz redundancia, e toda combinacao continua tendo a mesma
probabilidade individual. Precos oficiais sao responsabilidade do usuario. Jogos sem
preco (`price_status=unset`) rodam em modo contagem, como nos exemplos acima. Se um jogo
for marcado com precos de EXEMPLO (ilustrativos, nao oficiais), a guarda BLOQUEIA a
execucao a menos que voce passe `--allow-example-prices`, assumindo de forma explicita
que os valores nao sao oficiais. Precos oficiais (ex.: Quina) rodam sem a flag.

## Status

Repositorio publico. CI ao vivo via GitHub Actions
(`.github/workflows/ci.yml`: ruff + pytest a cada push) - o badge de CI acima reflete
o status do ultimo run na `main`. Suite atual: 158 testes; o badge de cobertura e atualizado pelo CI a cada push.
Detalhe de progresso em `docs/ROADMAP.md`.

## Contributing

Projeto pessoal, aberto ao publico. Forks sao bem-vindos; issues e pull requests
tambem - mas como e mantido por uma pessoa so, nao ha garantia de tempo de resposta
nem de manutencao ativa.

Ambiente de desenvolvimento (comandos reais, espelham o `Makefile`):

```bash
pip install -e ".[dev]"                        # engine + ferramentas de dev (make install)
pytest                                         # roda a suite de testes      (make test)
ruff check lottery_optimizer tests scripts     # lint                        (make lint)
```

Mudancas devem manter a suite verde e o ruff limpo - mesmo portao do CI
(`.github/workflows/ci.yml`). E precisam preservar o principio da engine: ela otimiza
cobertura combinatoria e reduz redundancia, e NUNCA preve sorteios - nada que sugira
aumento da chance individual de ganhar.

## Precos

Precos oficiais nao sao inclusos. Configure os precos vigentes na spec da loteria antes
de gerar apostas reais com orcamento monetario.
