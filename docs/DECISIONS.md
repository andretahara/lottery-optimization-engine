# DECISIONS - Architecture Decision Records

Formato ADR: Contexto / Decisao / Consequencia. Append-only; novas decisoes que
revertem antigas referenciam o ADR superado.

---

## ADR-001 - Linguagem: Python 3.12
- **Contexto**: Engine de combinatoria pesada + estatistica de carteira + export.
- **Decisao**: Python 3.12. `itertools`/`random` no nucleo, `numpy` p/ metricas vetoriais.
- **Consequencia**: Iteracao rapida e libs cientificas fortes. Performance bruta inferior
  a Rust em loterias enormes; mitigar com algoritmos (cobertura greedy) e numpy. Cliente externo
  consome via API futura se necessario.

## ADR-002 - Interface: biblioteca + CLI fino
- **Contexto**: Precisa ser reutilizavel e testavel sem acoplar a web.
- **Decisao**: Nucleo de funcoes puras importavel; CLI fino por cima. Sem servico HTTP no MVP.
- **Consequencia**: Alta testabilidade, baixo acoplamento. Exposicao web fica para fase futura
  (e exige defesa de endpoint antes de qualquer disparo cobrado).

## ADR-003 - Loteria como Spec configuravel, nunca hardcode
- **Contexto**: 8+ loterias com regras distintas (pool, marks, tiers, regras especiais).
- **Decisao**: `LotterySpec` (dataclass) + `registry` de presets. Logica le a spec; sem `if nome ==`.
- **Consequencia**: Adicionar loteria = adicionar config, nao codigo. Spec precisa modelar
  regras especiais (Lotomania marca 50 de 100; Dupla Sena 2 sorteios; Timemania time do coracao).

## ADR-004 - Sem sinal preditivo/historico (regra fundamental)
- **Contexto**: Falacia do apostador. Loteria justa = toda combinacao equiprovavel.
- **Decisao**: PROIBIDO quente/frio/atrasado/ciclo/data/numerologia/padrao historico/supersticao
  como sinal de selecao. Engine otimiza SO cobertura combinatoria e qualidade de carteira.
- **Consequencia**: Modulo de "estatistica descritiva sobre historico de sorteios" NAO existe.
  Metricas sao sobre a CARTEIRA GERADA (intra-portfolio), nao sobre sorteios passados. Frame
  honesto, defensavel legal/marca. Disclaimer obrigatorio em toda saida (ver ADR-005).

## ADR-005 - Disclaimer obrigatorio, constante unica
- **Contexto**: Risco de usuario interpretar otimizacao como previsao.
- **Decisao**: Constante unica em `disclaimer.py`; toda saida probabilistica (relatorio/export/CLI)
  injeta o texto exato definido em CLAUDE.md.
- **Consequencia**: Mensagem consistente, testavel (teste verifica presenca). Mudanca de texto
  num lugar so.

## ADR-006 - Precos configuraveis, nunca inventados
- **Contexto**: Precos oficiais mudam; inventar = informacao falsa.
- **Decisao**: `LotterySpec.price_table` = `None` placeholder. Gerar aposta real exige usuario setar.
  Funcoes de orcamento falham explicito/avisam se preco ausente.
- **Consequencia**: Sem numero falso. Custo: usuario precisa configurar antes de usar orcamento monetario.
  Orcamento por CONTAGEM de jogos funciona sem preco.

## ADR-007 - Sem acesso a rede no nucleo
- **Contexto**: Testabilidade e determinismo.
- **Decisao**: Nucleo nao busca dados (sem fetcher Caixa). Entrada de dados, quando existir, e
  arquivo (CSV/JSON) fornecido pelo usuario. Saida e export local.
- **Consequencia**: Testes deterministas e offline. Eventual ingestao de historico fica em ferramenta
  separada e opcional (e nunca alimenta selecao - ver ADR-004).

## ADR-008 - Layout src/ + pyproject + pytest
- **Contexto**: Empacotamento limpo e import isolado.
- **Decisao**: `src/lottery_engine/`, `pyproject.toml` (PEP 621), testes em `tests/` com pytest.
- **Consequencia**: Evita import acidental do cwd; instalavel via `pip install -e .`.

## ADR-009 - Conjunto documental como memoria duravel
- **Contexto**: Sessoes podem sofrer /clear ou crash; precisa sobreviver sem perda de contexto.
- **Decisao**: `CLAUDE.md` (operacional, relido toda sessao) + `docs/{SPEC,ARCHITECTURE,MATH_MODEL,ROADMAP,DECISIONS,TESTING}.md`.
  CLAUDE.md curto e linka os detalhados.
- **Consequencia**: Retomada barata e consistente. Custo: manter docs em sincronia com o codigo
  (gate de bloco exige atualizar ROADMAP/DECISIONS).

## ADR-010 - Garantia de wheeling provada por forca bruta
- **Contexto**: Covering designs vem de heuristica; afirmar garantia sem prova e perigoso.
- **Decisao**: Em casos pequenos, enumerar todos os sorteios possiveis e verificar a garantia 100%.
  Heuristica gera; teste de forca bruta PROVA.
- **Consequencia**: Confianca real na garantia para tamanhos testaveis; extrapolacao para tamanhos
  grandes documentada como propriedade do algoritmo, nao do teste.

## ADR-011 - `combinatorics` como modulo proprio
- **Contexto**: Varios modulos precisam de C(n,k), iteracao de combinacoes e k-subconjuntos.
- **Decisao**: Centralizar em `combinatorics.py` puro, reusado por spec/generate/wheels/metrics.
- **Consequencia**: Sem duplicacao; ponto unico de otimizacao/teste da combinatoria.

## ADR-012 - Determinismo via RNG com seed
- **Contexto**: Testes de geracao e otimizacao precisam ser reproduziveis.
- **Decisao**: Toda aleatoriedade passa por `rng.Rng(seed)`. Mesma seed => mesma saida.
- **Consequencia**: CI determinista, debugging viavel. Exige disciplina: nenhum `random` solto no nucleo.

## ADR-013 - Reestruturacao para pacote `lottery_optimizer` (supera ADR-008)
- **Contexto**: Bloco "esqueleto profissional" pediu arvore rica (core/metrics/algorithms/
  games/export/cli/utils) com layout flat. O pacote `lottery_engine` (src/) do Bloco 1 era
  mais simples e cobria so parte.
- **Decisao**: Adotar `lottery_optimizer/` flat na raiz. Portar a logica real do `lottery_engine`
  (combinatoria, validacao de spec, params das 8 -> 6 loterias) para `core/` e `games/`, e
  remover `src/lottery_engine`. Supera o layout src/ do ADR-008.
- **Consequencia**: Um unico pacote, decomposicao por responsabilidade. Nada de valor perdido
  (logica portada + testes reescritos). Custo: churn de Bloco 1, justificado pela estrutura alvo.

## ADR-014 - Modelos de dominio com pydantic
- **Contexto**: GameSpec/Ticket precisam de validacao robusta e imutabilidade.
- **Decisao**: pydantic v2 (`frozen=True`) para `GameSpec` e `Ticket`; `Portfolio` como classe
  comum (colecao mutavel controlada). Validacao via `model_validator`/`field_validator` levantando
  SpecError/TicketError (pydantic encapsula em ValidationError).
- **Consequencia**: Validacao declarativa e mensagens claras. Dep de runtime: pydantic.

## ADR-015 - 6 specs base; variantes de sorteio especial adiadas
- **Contexto**: O bloco de esqueleto listou 6 YAML (quina, mega_sena, lotofacil, lotomania,
  timemania, dupla_sena), sem Mega da Virada / Quina de Sao Joao.
- **Decisao**: Registrar as 6 base. Variantes especiais (Virada, Sao Joao) sao as mesmas specs
  + flags `special_draw/no_accumulation`; serao adicionadas como YAML quando necessario.
- **Consequencia**: Catalogo enxuto agora; extensao trivial (novo YAML, zero codigo).

## ADR-016 - Metricas normalizadas em [0, 1]
- **Contexto**: `score` ponderado (pesos somando 1) exige metricas comparaveis. Distancia crua
  (uniao - intersecao) e ilimitada e estourava o score acima de 1.
- **Decisao**: Distancia vira distancia de Jaccard normalizada |A^B|/|AvB| em [0,1]. Todas as
  metricas (coverage, distance, balance) ficam em [0,1] -> score em [0,1].
- **Consequencia**: Score interpretavel e limitado. Bug pego por teste (CLAUDE.md §7-8).

## ADR-017 - GameSpec por universo + allowed_ticket_sizes (supera ADR de campos do Bloco 1)
- **Contexto**: Bloco do nucleo pediu API explicita: game_id, universe_min/max, draw_size,
  allowed_ticket_sizes, price_table, prize_tiers, notes.
- **Decisao**: Reescrever GameSpec nesses campos. `allowed_ticket_sizes` (conjunto explicito)
  substitui min/max_marks - modela melhor jogos de tamanho fixo (Lotomania=50, Timemania=10)
  e faixas (Mega 6..15). `universe_min/max` substitui pool+number_start (Lotomania 0..99 natural).
- **Consequencia**: API mais expressiva e generica. Quebra a API do Bloco 1; YAML/registry/
  scripts/testes atualizados. Helpers derivados (`pool`, `min/max_ticket_size`) preservam ergonomia.

## ADR-018 - Cobertura com modos exact/streaming/sampled + trava de memoria
- **Contexto**: K-subsets de jogos grandes explodem (Lotomania C(50,20)~4.7e13). Exato e inviavel.
- **Decisao**: `CombinationCoverage` oferece exact (com `DEFAULT_EXACT_CAP`), streaming (lazy) e
  sampled (Monte Carlo via SeededRng). Probabilidade do premio principal usa cobertura UNICA.
- **Consequencia**: Escala para qualquer loteria sem estourar memoria; estimativas reproduziveis
  por seed. Custo: resultado amostral e aproximado (documentado, tolerancia em teste).

## ADR-019 - Custo oficial vs estimativa explicitamente marcada
- **Contexto**: Sem preco oficial para um tamanho, e tentador "preencher" - mas seria inventar.
- **Decisao**: `CostModel` retorna `CostResult(amount, is_estimate)`. Oficial so quando o tamanho
  esta na price_table; senao estima `base * C(T,K)` com `is_estimate=True`; sem base nem tabela, erro.
- **Consequencia**: Usuario sempre sabe o que e preco real vs estimativa. Reforca ADR-006.

## ADR-020 - Guarda de precos: bloqueia execucao real com preco nulo/exemplo
- **Contexto**: Inventar preco oficial e proibido (ADR-006). Mas precisamos permitir analise
  com precos ilustrativos sem arriscar que virem aposta real por engano.
- **Decisao**: GameSpec ganha `price_status` (unset|example|official), `official_price_last_checked`,
  `price_source_note`. `core/pricing.assert_prices_usable` bloqueia run real salvo status official;
  precos 'example' so passam com `--allow-example-prices`; 'unset'/null nunca passam. CostModel marca
  `is_estimate=True` para qualquer preco nao-oficial. Relatorio registra a config de preco usada.
- **Consequencia**: Impossivel disparar aposta real com preco inventado/ilustrativo sem consentimento
  explicito. Os 6 YAML vem com price_table null (precos NAO verificados neste ambiente); exemplos
  marcados EXAMPLE_NOT_OFFICIAL ficam so no user_overrides.example.yaml.

## ADR-021 - GameRegistry com overrides locais e jogos customizados (sem estado global)
- **Contexto**: Usuario precisa atualizar precos e criar jogos sem editar o pacote nem depender de rede.
- **Decisao**: `GameRegistry` e classe instanciavel (carrega YAML de um dir). `apply_overrides`/
  `load_overrides_file` sobrescrevem campos (revalidando), `add_custom` registra jogo novo. Funcoes
  de modulo `available()/get()` delegam a uma instancia default cacheada. Overrides nunca mutam o default.
- **Consequencia**: Reproduzivel e offline; precos do usuario entram por arquivo local. Arquivos
  non-game (user_overrides.example.yaml) sao ignorados no load.

## ADR-022 - Geracao balanceada simetrica (nao quebra equiprobabilidade)
- **Contexto**: "Balancear" a carteira pode parecer heuristica preditiva proibida.
- **Decisao**: RandomBalancedOptimizer balanceia a FREQUENCIA das dezenas na carteira de forma
  SIMETRICA: embaralha (desempate aleatorio) e escolhe as dezenas menos usadas ate aqui. Nenhuma
  dezena especifica e favorecida; so a representacao fica uniforme. Modo balanced=False da amostragem
  uniforme pura. Ambos sem quente/frio/historico.
- **Consequencia**: Reduz variancia de cobertura sem violar a regra fundamental nem prever sorteio.
  Justica do modo puro validada por teste qui-quadrado.

## ADR-023 - PortfolioScore parametrizavel; cobertura unica de K-subsets e o criterio principal
- **Contexto**: A funcao-objetivo precisa deixar explicito o que importa pro premio principal vs
  faixas secundarias, sem sugerir previsao.
- **Decisao**: `PortfolioScore` combina componentes em [0,1] (main_coverage = K-subsets UNICOS /
  C(N,K), intermediate = pares/trincas, diversity, balance, low_redundancy, budget_adherence) menos
  penalizacoes (duplicatas, concentracao, baixa distancia). Pesos configuraveis por YAML/JSON.
  main_coverage e o PRINCIPAL; balanceamento melhora diversidade/redundancia mas NAO preve sorteio;
  pesos altos em intermediate favorecem faixas secundarias.
- **Consequencia**: Objetivo transparente e auditavel (breakdown por componente). Metricas mantidas
  aditivas (funcoes simples do Bloco 1 preservadas para back-compat).

## ADR-024 - Geradores: pacote proprio, candidatos bounded, orcamento por contagem
- **Contexto**: Construir carteira inicial e tarefa distinta de otimizar; precisa escalar sem
  estourar memoria.
- **Decisao**: pacote `generators/` separado de `algorithms/`. `BaseGenerator.generate(spec, budget,
  constraints, seed)`; budget = numero de apostas (orcamento monetario exige preco oficial, bloqueado).
  Geradores gulosos (greedy_coverage/diversity) usam pool BOUNDED de candidatos aleatorios por slot
  (_CANDIDATES=40) -> nao enumeram o espaco. Estrategias all_simple/fixed/mixed_ticket_sizes.
- **Consequencia**: Reprodutivel por seed, sem duplicatas, sem explosao. Greedy/diversity sao
  heuristicas (nao otimo global) - aceitavel para carteira inicial; otimizadores refinam depois.

## ADR-025 - Otimizadores: BaseOptimizer/OptimizationResult, movimentos seguros, score=PortfolioScore
- **Contexto**: Refinar a carteira inicial sem violar orcamento/duplicatas/universo.
- **Decisao**: `BaseOptimizer.optimize(initial, spec, budget, score_config, runtime_config, seed)
  -> OptimizationResult` (best/initial/improvement/iterations/elapsed/score_history/accepted/
  rejected/checkpoint/logs). Movimentos (troca de dezena, troca de aposta, replace-worst) preservam
  contagem e validade e nunca criam duplicata. Todos os otimizadores inicializam best=carteira
  inicial -> nunca pioram. coverage_mode 'auto' (exact com fallback sampled). SeededRng -> reprodutivel.
  Antigo algorithms/Optimizer (random_balanced) removido: virou generators (BalancedRandomGenerator).
- **Consequencia**: 5 otimizadores (LocalSearch/SA/Genetic/GRASP/Hybrid) com contrato unico.
  Custo: score com cobertura exata e caro (replace-worst chama scorer N vezes); perf sera tratada
  no bloco de auditoria de engenharia (cache/sampled/limites).

## ADR-026 - Export: assembler ReportData unico para TXT/Excel/graficos
- **Contexto**: TXT, Excel e graficos precisam das mesmas metricas; recalcular em cada um duplica.
- **Decisao**: `export/report_data.build_report_data` monta um `ReportData` (cobertura modo auto,
  frequencia, equilibrio, distancia, custo/saldo via cost_model, metadados algoritmo/seed/timestamp/
  config-de-preco). TXT e Excel consomem esse objeto; graficos usam matplotlib (Agg, sem seaborn,
  figura por grafico). CSV colunar com dezenas ordenadas. Disclaimer no TXT e na aba AvisoMatematico.
- **Consequencia**: Uma fonte de verdade para o relatorio. Custo: cobertura no relatorio usa exact
  (fallback sampled) - caro em jogos enormes, aceitavel para export pontual.

## ADR-027 - CLI: orcamento por contagem; bloqueio de preco de exemplo; output datado
- **Contexto**: A CLI precisa ser usavel sem precos oficiais (que sao do usuario) mas sem permitir
  aposta real com preco enganoso.
- **Decisao**: `--budget` = numero de apostas (modo por contagem, sem preco). `_check_real_run`
  bloqueia jogo com price_status='example' sem `--allow-example-prices` (preco unset e ok no modo
  contagem, custo aparece 'n/d'). Saidas em `output/YYYYMMDD_HHMMSS_GAME_ID/` com config.log. Todo
  comando imprime o aviso matematico. 9 comandos (list-games/inspect-game/validate-config/generate/
  optimize/report/export/compare/benchmark).
- **Consequencia**: Fluxo completo testavel offline via CliRunner; orcamento monetario fica nos
  scripts de exemplo (que exigem preco oficial). Benchmark base em `benchmark.py` (bloco Benchmark enriquece).

## ADR-028 - Exemplos operacionais com config de execucao separada da game spec
- **Contexto**: Rodar um caso real (orcamento monetario) exige preco oficial + decisao de tamanho
  de aposta, sem inventar preco e sem prender a engine a um jogo.
- **Decisao**: Config de EXECUCAO em `configs/*.yaml` (game_id, budget, optimizer, score_weights,
  output_dir + campos de preco como override). `scripts/run_quina_sao_joao.py` valida preco
  (`assert_prices_usable`, PARA se null/exemplo sem flag), calcula num_tickets = budget // preco
  simples, e demonstra que multiplas com custo/combinacao igual NAO aumentam eficiencia. Testes
  usam preco FICTICIO marcado example (nunca como oficial).
- **Consequencia**: Fluxo real reproduzivel e auditavel; preco continua responsabilidade do usuario.

## ADR-029 - Runner generico unico para os scripts de exemplo (anti-duplicacao)
- **Contexto**: Quina de Sao Joao e Mega da Virada compartilham 100% do fluxo (carregar spec,
  validar preco, decidir tamanho, gerar, otimizar, exportar). Duplicar seria divida tecnica.
- **Decisao**: `lottery_optimizer/runner.run_from_config(config, ...)` concentra o fluxo, parametrizado
  por game_id e pesos. Os scripts `run_quina_sao_joao.py` e `run_mega_sena_virada.py` viram wrappers
  finos (config default + main). Teste anti-hardcode garante que algorithms/generators/core/metrics
  nao mencionam loteria especifica.
- **Consequencia**: Zero duplicacao de logica; trocar de jogo = trocar game_id+pesos no YAML.
  Prova de que a engine e generica (N=80 K=5 vs N=60 K=6 sem mudar codigo).

## ADR-030 - Auditoria matematica (sem features novas): invariantes travados
- **Contexto**: Antes de seguir, auditar correcao de probabilidade/custo/carteira/metricas/
  otimizadores/relatorios.
- **Achados**:
  1. Probabilidade: C(N,K) correto (Quina/Mega/Lotofacil); premio principal usa cobertura UNICA
     (nao bruta); sem dupla contagem (dedup real); p_main <= 1 sempre. OK.
  2. Custo: respeita price_table; estimativas marcadas (is_estimate); run real bloqueado sem preco
     oficial; saldo correto. OK.
  3. Carteira: duplicatas detectadas; dezena fora do universo e tamanho invalido rejeitados.
     ACHADO (nao-bug): erro de `Ticket` sobe como `pydantic.ValidationError` (encapsula TicketError),
     enquanto `Portfolio.add` sobe `TicketError` direto - inconsistencia de tipo de excecao. Caller
     deve tratar ambos. Documentado; nao quebra invariante.
  4. Metricas: cobertura/Jaccard/redundancia/frequencia ideal corretas. OK.
  5. Otimizadores: orcamento preservado, sem duplicatas, GameSpec preservado, nunca pioram
     (best>=initial) para os 5 otimizadores. OK.
  6. Relatorios: contem disclaimer e "probabilidade teorica"; sem "garantia de premio"/"vai ganhar".
     OK.
- **Decisao**: travar tudo em `tests/test_audit_math.py` (15 testes). Nenhum bug critico de matematica.
  Pendencia conhecida para o bloco de performance: `coverage_ratio` itera C(N,size) para contar o
  total (lento no caminho do score dos otimizadores) - correto, mas caro.
- **Consequencia**: Base matematica verificada e protegida contra regressao.

## ADR-031 - Auditoria de engenharia/performance: memoizacao + modos de memoria + logs
- **Contexto**: Otimizadores eram lentos (~100s na suite). Causa: `coverage_ratio` ITERAVA C(N,size)
  para contar o total e o scorer recomputava cobertura exata a cada candidato.
- **Decisao** (sem sacrificar correcao):
  1. `coverage_ratio`: total via `n_choose_k(pool, size)` (formula, nao iteracao).
  2. `make_scorer`: memoiza por assinatura da carteira (frozenset de jogos) - mesma carteira nao
     reavalia cobertura. Resultado identico, so mais rapido.
  3. `CombinationCoverage(exact_cap)` + `count_unique_auto`: exato dentro da trava; senao ESTIMATIVA
     amostral COM LOG (nunca silenciosa). `max_memory_mode='conservative'` baixa a trava (100k) p/
     cair em amostral mais cedo e evitar estouro de memoria. Plumbado por RuntimeConfig ->
     make_scorer -> PortfolioScore -> CoverageMetrics. CLI `--max-memory-mode`.
  4. `utils/profiling.profile_block`: tempo + pico de memoria (tracemalloc).
  5. `get_logger` propaga (caplog testavel; root sem handler nao duplica).
- **Consequencia**: Suite 100s -> 11.5s, mesmos resultados. Estimativa sempre logada (auditavel).
  Modo conservador protege jogos grandes (Lotomania) sem quebrar a matematica.

## ADR-032 - Benchmark: vencedor so entre carteiras validas, com memoria e exports
- **Contexto**: Comparar geradores e otimizadores de forma justa, sem premiar carteira invalida.
- **Decisao**: `run_benchmark` roda os 8 algoritmos (random/balanced_random/greedy_coverage +
  local_search/SA/genetic/grasp/hybrid) na mesma seed/orcamento/GameSpec, media sobre seeds.
  Metricas: score, melhoria, cobertura principal/pares/trincas/quadras, redundancia, distancia
  media, tempo e pico de memoria (profile_block). Vencedor = maior score SO entre carteiras
  validas (orcamento/duplicata/universo/tamanho); invalidas descartadas. Exports: benchmark.csv,
  benchmark.xlsx (+aba AvisoMatematico), benchmark_report.txt (com disclaimer e nota de validade),
  benchmark_score.png, benchmark_coverage.png.
- **Consequencia**: Comparacao reproduzivel e honesta; score sozinho nao decide.

## ADR-033 - Revisao de producao (2o engenheiro): findings + checklist
- **Findings**:
  - CRITICAL/HIGH: nenhum. Invariantes de orcamento/duplicata/universo/disclaimer/premio-unico ja
    travados por auditoria.
  - MEDIUM-1 (CORRIGIDO): relatorio nao distinguia probabilidade exata de estimada. Agora a linha da
    probabilidade recebe "[ESTIMADA - cobertura amostral]" quando coverage_mode_used == sampled.
  - MEDIUM-2 (CORRIGIDO): `GeneticOptimizer._crossover` preenchia faltas com tamanho fixo
    `len(pa[0])` - quebrava carteiras de tamanhos mistos. Agora amostra o tamanho da distribuicao
    dos pais (suporta mixed_ticket_sizes).
  - MEDIUM-3 (VERIFICADO): `p_tier_portfolio_approx` (cota de Boole) e LIMITE SUPERIOR e pode
    inflar - teste garante que e >= prob single e NUNCA aparece no relatorio ao usuario.
  - LOW (documentado): nomes duplicados `total_outcomes`/`total_combinations` e
    `simple_combinations`/`equivalent_simple_games` (mesmo C(.,.)) - mantidos por compat, sem risco.
- **Checklist de producao**: [x] testes verdes (146) [x] ruff limpo [x] sem preco oficial inventado
  (null por default + guarda) [x] disclaimer em CLI/relatorio/Excel [x] relatorio nao promete
  previsao/garantia [x] estimativa nunca silenciosa [x] otimizadores preservam orcamento e nao
  duplicam [x] engine generica (teste anti-hardcode) [x] reprodutivel por seed [x] CSV/Excel abrem.
- **Consequencia**: PR aprovavel; nenhum finding critical/high pendente.
