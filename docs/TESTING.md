# TESTING - Estrategia de testes

Tudo via `pytest`. Nenhuma feature e "feita" sem teste verde correspondente (CLAUDE.md §7-8).
Determinismo por seed fixa. Garantias combinatorias provadas, nao assumidas.

## 1. Comandos

```bash
pytest -q                          # tudo
pytest tests/test_wheels.py -q     # um modulo
pytest -q -k coverage              # por expressao
pytest -q --maxfail=1 -x           # parar no primeiro erro (debug)
```

## 2. Camadas de teste

### a. Unitarios (`tests/test_<modulo>.py`)
Cada funcao do nucleo com casos normais + borda. Ex.: `combinatorics.n_choose_k` em valores
conhecidos (C(60,6)=50063860); `spec.validate()` aceita specs validas e rejeita invalidas
(draw_size>pool, marks fora de ordem); `registry.get` retorna as 8 loterias.

### b. Propriedade (hypothesis)
Invariantes que valem para entradas geradas:
- Todo ticket gerado: T dezenas distintas, ordenadas, dentro de `[1, pool]`.
- Carteira sem duplicatas (default).
- `n_choose_k(n,k) == n_choose_k(n, n-k)`.
- Geracao respeita orcamento: nunca mais jogos que o permitido.
- Wheel: garantia se mantem para qualquer subconjunto sorteado simulado.

### c. Garantia combinatoria por forca bruta (wheeling)
Para casos PEQUENOS (ex.: pool 9, draw 3, garantia simples), enumerar TODOS os
`C(M, K')` sorteios possiveis e verificar que a wheel cumpre a garantia em 100% deles.
Prova a corretude do covering design sem confiar na heuristica.

### d. Uniformidade estatistica (geracao justa)
Amostra grande sob seed fixa; teste qui-quadrado de frequencia das dezenas e ausencia de
vies posicional. Tolerancia calibrada; objetivo e detectar vies grosseiro, nao ruido fino.

### e. Integracao (fluxo ponta-a-ponta)
`registry -> generate/wheel -> portfolio -> metrics -> export`, validando que o pipeline roda
para cada loteria-alvo e produz carteira coerente com a spec.

### f. Export
- CSV: parse de volta, conferir linhas/colunas e numeros.
- Excel: abrir com openpyxl, conferir celulas.
- Relatorio: presenca OBRIGATORIA do texto do disclaimer (string exata de `disclaimer.py`).
- Robustez: caracteres/precos None tratados sem quebrar.

### g. Reprodutibilidade
Mesma seed + mesmos parametros => carteira identica (igualdade exata). Seeds diferentes =>
carteiras diferentes. Garante CI determinista e debugging.

## 3. Regressao matematica (anti-previsao)
Teste-guarda que afirma propriedades da regra fundamental:
- Probabilidade de premio principal de carteira de M jogos distintos == `M / C(N,K)` (modelo).
- Nenhum modulo expoe API de "numero quente/frio/atrasado" (checagem de superficie do pacote).

## 4. Convencoes
- Fixtures de specs pequenas (`mini lottery` pool 9 draw 3) para forca bruta barata.
- Seed padrao de teste fixa (ex.: 12345). Sem dependencia de relogio/rede.
- Cobertura alvo: nucleo combinatorio e wheeling com cobertura alta; export e cli com
  smoke tests. Sem perseguir 100% cego.

## 5. Gate de bloco
Antes de fechar qualquer Bloco do ROADMAP: rodar `pytest -q` do escopo, colar resultado
no resumo, commitar so com verde. Vermelho = bug a corrigir, nunca "retry".
