# SPEC - Lottery Optimization Engine

## 1. Proposito

Biblioteca Python generica que gera e avalia carteiras de apostas para loterias
combinatorias. Otimiza COBERTURA combinatoria e qualidade estrutural da carteira sob
um orcamento. Nao preve sorteios. Nao altera a probabilidade individual de qualquer
combinacao (ver `docs/MATH_MODEL.md`).

## 2. Escopo

Inclui:
- Modelo de loteria configuravel (`LotterySpec`) cobrindo Quina, Quina de Sao Joao,
  Mega-Sena, Mega-Sena da Virada, Lotofacil, Lotomania, Timemania, Dupla Sena e futuras.
- Geracao de jogos uniformemente justa (sem vies).
- Wheeling / covering designs com garantia K-de-M verificavel.
- Otimizacao de carteira: diversidade, baixa sobreposicao, distancia, balanco, redundancia.
- Metricas de avaliacao de carteira (intra-carteira).
- Export CSV / Excel / relatorio, sempre com o disclaimer obrigatorio.
- CLI fino.

Fora de escopo (nao-objetivos):
- Previsao de numeros, analise de sorteios passados, sinais "quente/frio/atrasado".
- Busca de dados em rede (sem fetcher).
- Precos oficiais embutidos.
- Servico HTTP / web (fase futura, fora deste repo por ora).

## 3. Conceitos e vocabulario

- **N (pool)**: maior dezena do universo (ex.: Mega-Sena N=60).
- **K (draw / sorteio)**: quantas dezenas sao sorteadas (ex.: Mega-Sena K=6).
- **T (marks / aposta)**: quantas dezenas o apostador marca, `K <= T <= T_max`.
- **Tier (faixa de premio)**: numero de acertos que paga (ex.: 4, 5, 6 na Mega).
- **Jogo / ticket**: um conjunto de T dezenas distintas.
- **Carteira / portfolio**: conjunto de jogos comprado de uma vez.
- **Wheel (roda)**: carteira estruturada que garante cobertura minima de subconjuntos.
- **Cobertura**: quais combinacoes de tamanho K (ou subconjuntos menores) a carteira contem.

## 4. Modelo de loteria (`LotterySpec`)

Campos (config, nunca hardcode em logica):
- `name: str`
- `pool: int` (N)
- `draw_size: int` (K)
- `min_marks: int`, `max_marks: int` (faixa de T; aposta simples = `min_marks == K` na maioria;
  Lotomania marca 50 fixo num pool de 100 com K=20; modelar via min/max + draw_size)
- `prize_tiers: list[int]` (quantidades de acerto que premiam, ordenadas)
- `price_table: dict[int, Decimal] | None` (preco por quantidade de marcas; `None` ate o usuario setar)
- `extra_rules: dict` (gancho p/ regras especiais: Dupla Sena dois sorteios; Timemania "time
  do coracao"; Mega da Virada nao acumula 1a faixa). Modelado declarativamente, sem ramificar por nome.

Validacao obrigatoria: `0 < draw_size <= min_marks <= max_marks <= pool`; tiers dentro de
`[algum_min, max_marks]`; pool/draw coerentes.

## 5. Capacidades funcionais

1. **Gerar carteira aleatoria justa** sob orcamento (contagem de jogos ou valor, se preco setado).
2. **Gerar wheel** com garantia "se K' dos meus M numeros sairem, garante >= 1 jogo com J acertos".
3. **Otimizar carteira** existente/gerada para maximizar diversidade e cobertura, minimizar redundancia.
4. **Avaliar carteira**: relatorio de metricas (ver `metrics`).
5. **Exportar**: CSV, Excel, relatorio textual - com disclaimer.

## 6. Restricoes e invariantes

- Toda saida probabilistica carrega o disclaimer (constante unica).
- Nenhum jogo tem dezenas repetidas; nenhuma carteira tem jogos duplicados (salvo se o
  usuario explicitamente permitir, default proibe).
- Determinismo sob seed fixa (reprodutibilidade de testes e de geracoes).
- Sem efeitos de rede, sem I/O implicito fora de export explicito.

## 7. Criterios de sucesso

- Specs das 8 loterias-alvo carregam e validam.
- Geracao justa passa em teste estatistico de uniformidade (chi-quadrado sob seed/amostra grande).
- Garantia de wheeling provada por forca bruta em casos pequenos.
- Carteira otimizada supera baseline aleatoria em metricas de cobertura/sobreposicao.
- Exports integros e com disclaimer; pytest verde ponta-a-ponta.
