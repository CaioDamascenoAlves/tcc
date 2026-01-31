# Relatório: Preparação de Dados e Geração de Redes

**Data:** 31 de Janeiro de 2026
**Contexto:** TCC - Análise de Redes Complexas no Esporte Olímpico

---

## 1. Limpeza e Normalização de Dados

### 1.1 Problemas Identificados no Dataset Original

**Eventos históricos obsoletos:**
- Eventos em yards (1904): 8 eventos, 52 registros
- Natação subaquática, para marinheiros, "Plunge for Distance": 3 eventos
- Distâncias antigas únicas (300m, 500m, 1,200m, 4,000m): 11 eventos

**Inconsistências de nomenclatura:**
- "Swimming Men's 100 metres Freestyle" (1896-2016) vs "Men's 100m Freestyle" (2021)
- "Judo Men's Lightweight" (1964-2016) vs "Men -66 kg" (2021)
- "Boxing Men's Heavyweight" vs "Men's Heavy (81-91kg)"

**Total removido:** 190,979 registros (70.18%) - maioria de outros esportes não selecionados

### 1.2 Normalizações Aplicadas

**Padronizações:**
- ✅ `metres` → `m`
- ✅ Removido prefixo redundante "Swimming/Judo/Boxing Men's/Women's"
- ✅ Adicionado prefixo padronizado `M/F` baseado no sexo
- ✅ Vírgulas removidas de números (1,500 → 1500)

**Mapeamento de eventos que mudaram de nome:**

**Judô:**
| Nome Antigo | Nome Normalizado |
|-------------|------------------|
| Extra-Lightweight M | M -60kg |
| Half-Lightweight M | M -66kg |
| Lightweight M | M -73kg |
| Half-Middleweight M | M -81kg |
| Middleweight M | M -90kg |
| Half-Heavyweight M | M -100kg |
| Heavyweight M | M +100kg |

**Boxe:**
| Nome Antigo | Nome Normalizado |
|-------------|------------------|
| Flyweight M | M Fly (48-52kg) |
| Bantamweight M | M Bantam (52-57kg) |
| Welterweight M | M Welter (63-69kg) |
| Middleweight M | M Middle (69-75kg) |
| Super-Heavyweight M | M Super Heavy (+91kg) |

### 1.3 Dataset Final Limpo

**Estatísticas:**
- **Total de registros:** 83,497
- **Atletas únicos:** 48,949
- **Anos cobertos:** 1896 - 2021
- **Esportes:** 6 (Swimming, Basketball, Football, Athletics, Judo, Boxing)
- **Eventos normalizados únicos:** 173

**Arquivos gerados:**
- `data/athlete_events_cleaned.csv` - Dataset limpo
- `data/event_normalization_mapping.csv` - Mapeamento de transformações

---

## 2. Análise de Eventos Icônicos

### 2.1 Metodologia

**Iconic Score = 0.35 × Edições + 0.15 × Países + 0.15 × Atletas + 0.35 × Longevidade**

Onde:
- **Edições:** Número de olimpíadas em que o evento esteve presente (normalizado)
- **Países:** Número de países diferentes que conquistaram medalhas (normalizado)
- **Atletas:** Número de atletas únicos medalhistas (normalizado)
- **Longevidade:** Anos entre primeira e última aparição (normalizado)

### 2.2 Top 5 Eventos por Esporte

#### 🏃 Atletismo
| Score | Evento | Edições | Anos |
|-------|--------|---------|------|
| 0.891 | M Marathon | 30 | 1896-2021 |
| 0.869 | M 800m | 30 | 1896-2021 |
| 0.862 | M Triple Jump | 30 | 1896-2021 |
| 0.861 | M 1500m | 30 | 1896-2021 |
| 0.858 | M High Jump | 30 | 1896-2021 |

**Nota:** M 100m tem score 0.827, mas é culturalmente o mais icônico ("homem mais rápido do mundo").

#### 🏊 Natação
| Score | Evento | Edições | Anos |
|-------|--------|---------|------|
| 0.934 | M 4 x 200m Freestyle Relay | 26 | 1908-2021 |
| 0.879 | **M 100m Freestyle** | 28 | 1896-2021 |
| 0.850 | F 4 x 100m Freestyle Relay | 25 | 1912-2021 |
| 0.832 | M 400m Freestyle | 27 | 1906-2021 |
| 0.821 | M 200m Breaststroke | 26 | 1908-2021 |

**Destaque:** M 100m Freestyle é considerado o "Blue Ribbon Event" da natação.

#### ⚽ Futebol
| Score | Evento | Edições | Anos |
|-------|--------|---------|------|
| 1.000 | M Football Men's Football | 28 | 1900-2021 |
| 0.230 | F Football Women's Football | 7 | 1996-2021 |

#### 🏀 Basquete
| Score | Evento | Edições | Anos |
|-------|--------|---------|------|
| 1.000 | M Basketball Men's Basketball | 20 | 1936-2021 |
| 0.594 | F Basketball Women's Basketball | 12 | 1976-2021 |

#### 🥋 Judô
| Score | Evento | Edições | Anos |
|-------|--------|---------|------|
| 1.000 | M -90kg | 13 | 1964-2016 |
| 0.984 | M -73kg | 13 | 1964-2016 |
| 0.972 | M +100kg | 13 | 1964-2016 |
| 0.898 | M -100kg | 12 | 1972-2016 |
| 0.882 | M -81kg | 12 | 1972-2016 |

#### 🥊 Boxe
| Score | Evento | Edições | Anos |
|-------|--------|---------|------|
| 1.000 | M Welter (63-69kg) | 25 | 1904-2021 |
| 0.958 | M Fly (48-52kg) | 25 | 1904-2021 |
| 0.897 | M -90kg | 25 | 1904-2016 |
| 0.895 | M Bantam (52-57kg) | 25 | 1904-2016 |
| 0.894 | M Feather (52-57kg) | 24 | 1904-2021 |

---

## 3. Referências Web sobre Eventos Icônicos

### 3.1 Atletismo 100m - "Blue Ribbon Event"

**Por que é o mais icônico:**
- Introduzido em 1896, equivalente moderno do antigo "stadion"
- Simplicidade universal: correr em linha reta o mais rápido possível
- Brevidade dramática (~10 segundos)
- O campeão é coroado "homem/mulher mais rápido(a) do mundo"

**Dados de audiência:**
- **20 milhões de espectadores** (Londres 2012, UK) - evento mais assistido
- **3º evento mais visualizado** nos EUA (Londres 2012)

**Fonte:** [100 metres at the Olympics - Wikipedia](https://en.wikipedia.org/wiki/100_metres_at_the_Olympics)

### 3.2 Natação 100m Livre - "Blue Ribbon Event"

**Status:**
- Evento destaque da natação, simboliza pura velocidade
- Similar ao 100m no atletismo
- Dawn Fraser (AUS): única mulher a vencer 3x

**Performance Paris 2024:**
- Pan Zhanle: recorde mundial **46.40s**
- Primeira vez: todos os 8 finalistas < 48s

**Fonte:** [100 metre freestyle - Wikipedia](https://en.wikipedia.org/wiki/100_metre_freestyle)

### 3.3 Audiência Olímpica Global (Paris 2024)

**Estatísticas globais:**
- **5 bilhões de pessoas** acompanharam (84% audiência potencial global)
- **28.7 bilhões de horas** de conteúdo visualizado (+25%)
- **23.5 bilhões de minutos** em streaming (+40%)

**Esportes mais seguidos:**
- **Natação:** esporte mais seguido globalmente
- **Ginástica:** 42% preferência americana, 80M+ espectadores
- **Basquete:** final masculina 19.5M espectadores
- **Futebol feminino:** +78% crescimento, 9M na final

**Fontes:**
- [Olympics.com - Paris 2024 Viewership](https://www.olympics.com/ioc/news/around-5-billion-people-84-per-cent-of-the-potential-global-audience-followed-the-olympic-games-paris-2024)
- [Sports Video Group - Paris 2024 Ratings](https://www.sportsvideo.org/2024/08/13/ratings-roundup-2024-paris-olympics-sweep-ratings-across-all-platforms-up-82-from-tokyo/)

---

## 4. Geração de Redes

### 4.1 Modelagem Adotada

**Tipo:** Rede Direcionada
**Agrupamento:** (Year, Event_Normalized)
**Lógica:** Competição direta no mesmo pódio

**Arestas:**
- Direção: Perdedor → Vencedor
- Pesos (eventos individuais):
  - Ouro → Bronze: peso 5
  - Ouro → Prata: peso 3
  - Prata → Bronze: peso 2
- Pesos (eventos de equipe): reduzidos em 20%

### 4.2 Resultados da Geração

**Total:** 178 redes geradas

**Por esporte:**
- Athletics: 87 redes
- Swimming: 38 redes
- Judo: 30 redes
- Boxing: 19 redes
- Basketball: 2 redes
- Football: 2 redes

**Conectividade:**
- **Conectadas:** 57 redes (32.0%)
- **Fragmentadas:** 121 redes (68.0%)

**Interpretação da fragmentação:**
A fragmentação é esperada e reflete:
1. Especialização esportiva (velocistas ≠ maratonistas)
2. Separação temporal (gerações diferentes não competem juntas)
3. Natureza da modelagem (Year+Event agrupa apenas pódios diretos)

### 4.3 Exemplos de Redes Geradas

**Redes Conectadas (análise profunda viável):**
- M 100m Freestyle (Swimming): 68 nós, 81 arestas
- M Marathon (Athletics): 84 nós, 89 arestas
- M Basketball Men's Basketball: 592 nós, 8,515 arestas
- M Football Men's Football: 1,275 nós, 21,620 arestas

**Redes Fragmentadas (reflexo metodológico):**
- M 100m (Athletics): 78 nós, 91 arestas, 18 componentes
- F 100m Freestyle (Swimming): 69 nós, 75 arestas, 18 componentes

---

## 5. Recomendações para o TCC

### 5.1 Casos de Estudo para Análise Profunda (texto)

**12 eventos em 6 PARES MASCULINO/FEMININO cobrindo TODOS os 6 esportes:**

Baseado em Iconic Score + popularidade cultural + representatividade de gênero.

#### **Par 1: Futebol (M+F):**

1. **M Football** (1900-2021, 28 edições)
   - 1,275 nós, 21,620 arestas, Score 1.000

2. **F Football** (1996-2021, 7 edições)
   - 293 nós, 6,285 arestas, Score 0.230
   - Crescimento +78% audiência (Paris 2024)
   - **Gap histórico: 96 anos**

#### **Par 2: Basquete (M+F):**

3. **M Basketball** (1936-2021, 20 edições)
   - 592 nós, 8,515 arestas, Score 1.000
   - Dream Team 1992, final Paris 2024: 19.5M espectadores

4. **F Basketball** (1976-2021, 12 edições)
   - 323 nós, 4,793 arestas, Score 0.594
   - Crescimento +43% audiência (Paris 2024)
   - **Gap histórico: 40 anos**

#### **Par 3: Atletismo - 100m (M+F):**

5. **M 100m** (1896-2021, 30 edições)
   - **"Blue Ribbon Event"** - homem mais rápido do mundo
   - 78 nós, 91 arestas, Score 0.827
   - 20M+ espectadores (Londres 2012)

6. **F 100m** (1928-2021)
   - 55 nós, 64 arestas, Score 0.827
   - "Mulher mais rápida do mundo", Florence Griffith-Joyner
   - **Gap histórico: 32 anos**

#### **Par 4: Natação - 100m Livre (M+F):**

7. **M 100m Freestyle** (1896-2021, 28 edições)
   - **"Blue Ribbon Event"** da natação
   - 68 nós, 81 arestas, Score 0.879
   - Recordista: Pan Zhanle 46.40s (Paris 2024)

8. **F 100m Freestyle** (1912-2021, 25 edições)
   - 69 nós, 75 arestas, Score 0.761
   - Dawn Fraser (AUS): única tricampeã olímpica
   - **Gap histórico: 16 anos**

#### **Par 5: Judô - Peso Médio (M+F):**

9. **M -90kg** (1964-2016, 13 edições)
   - 49 nós, 65 arestas, Score 1.000
   - 24 países medalhistas

10. **F -70kg** (1992-2016, 7 edições)
    - 22 nós, 34 arestas, Score 0.499
    - 13 países medalhistas
    - **Gap histórico: 28 anos**

#### **Par 6: Boxe - Peso Médio/Welter (M+F):**

11. **M Welter (63-69kg)** (1904-2021, 25 edições)
    - 150 nós, 363 arestas, Score 1.000
    - 47 países medalhistas - categoria mais global

12. **F Middle (69-75kg)** (2012-2016, 2 edições)
    - 7 nós, 10 arestas, Score 0.063
    - Rede CONECTADA (única!)
    - **Gap histórico: 108 anos - o maior!**

### 5.2 Estratégia de Apresentação

**No texto do TCC:**
- Análise qualitativa profunda dos **12 eventos (6 pares M/F)**
- **Foco em análise de gênero:** comparar padrões entre M e F em cada esporte
- Explicar comunidades detectadas (eras históricas? gerações? países dominantes?)
- Aplicar PageRank, HITS, Louvain, métricas de centralidade
- Contextualizar fragmentação estrutural como descoberta metodológica válida
- **1 seção por esporte** com análise M, análise F, e comparação M vs F

**Estrutura sugerida do capítulo de resultados:**
```
4. Resultados

  4.1 Esportes Coletivos
    4.1.1 Futebol
      - Análise M Football
      - Análise F Football
      - Comparação M vs F (gap 96 anos)

    4.1.2 Basquete
      - Análise M Basketball
      - Análise F Basketball
      - Comparação M vs F (gap 40 anos)

  4.2 Atletismo - Sprint (100m)
    - Análise M 100m ("homem mais rápido")
    - Análise F 100m ("mulher mais rápida")
    - Comparação M vs F (gap 32 anos)
    - Blue Ribbon Event

  4.3 Natação - 100m Livre
    - Análise M 100m Freestyle
    - Análise F 100m Freestyle
    - Comparação M vs F (gap 16 anos - menor!)
    - Blue Ribbon Event da natação

  4.4 Esportes de Combate
    4.4.1 Judô (Peso Médio)
      - Análise M -90kg
      - Análise F -70kg
      - Comparação M vs F (gap 28 anos)

    4.4.2 Boxe (Peso Médio/Welter)
      - Análise M Welter
      - Análise F Middle
      - Comparação M vs F (gap 108 anos - maior!)

  4.5 Síntese Cross-Esporte
    - Padrões de gênero (gap histórico médio: 53 anos)
    - Evolução temporal (crescimento recente feminino)
    - Fragmentação vs conectividade
    - Países dominantes por esporte e gênero
```

**No dashboard interativo:**
- Todas as 178 redes disponíveis para exploração
- Filtros por esporte, ano, tipo de medalha, conectividade
- Visualizações interativas com destaque para os 8 casos de estudo
- Seção "Explore mais" para os outros 170 eventos

**Seção de metodologia:**
- Justificar escolha dos 8 eventos com base em:
  - **Iconic Score** (dados objetivos: edições, países, atletas, longevidade)
  - **Audiência/popularidade** (referências web, dados de viewership)
  - **Representatividade** (todos os 6 esportes, mix coletivo/individual)
  - **Diversidade de rede** (redes conectadas vs fragmentadas, tamanhos variados)

---

## 6. Arquivos Gerados

**Dados:**
- `data/athlete_events_cleaned.csv` - Dataset limpo (83,497 registros)
- `data/event_normalization_mapping.csv` - Mapeamento de normalizações

**Análises:**
- `results/iconic_events_analysis.csv` - Iconic Score de todos eventos
- `results/event_names_investigation.txt` - Investigação de inconsistências

**Redes:**
- `results_per_event_cleaned/` - 178 redes em formato GEXF
- `results_per_event_cleaned/networks_summary.csv` - Resumo de todas as redes

**Scripts:**
- `src/data_cleaning/01_investigate_event_names.py` - Investigação
- `src/data_cleaning/02_normalize_event_names.py` - Normalização
- `src/data_cleaning/03_analyze_iconic_events.py` - Análise de Iconic Score
- `src/pipeline/02_network_generation_cleaned_data.py` - Geração de redes

---

## 7. Próximos Passos

1. ✅ **Dados limpos e normalizados**
2. ✅ **Eventos icônicos identificados**
3. ✅ **Redes geradas**
4. ⏳ **Análise de métricas de rede** (PageRank, HITS, Louvain, Betweenness)
5. ⏳ **Visualizações** para os 6 casos de estudo
6. ⏳ **Integração com dashboard**
7. ⏳ **Redação do texto** com análise qualitativa profunda

---

**Relatório compilado por:** Claude Sonnet 4.5
**Data:** 31 de Janeiro de 2026
