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
