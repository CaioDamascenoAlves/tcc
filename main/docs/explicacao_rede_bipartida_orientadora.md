# Explicação: Rede Bipartida para Análise de Rivalidades Olímpicas

**Texto preparado para áudio/mensagem à orientadora**

---

Professora, boa tarde!

Estou entrando em contato para discutir uma mudança metodológica importante que identifiquei no trabalho. Durante a análise dos resultados, percebi que a modelagem atual - que cria uma rede direcionada conectando atletas do mesmo pódio - apresenta **fragmentação estrutural** em esportes individuais. Isso acontece porque atletas que competem em eventos diferentes (por exemplo, um velocista de 100m e um saltador de vara no atletismo) nunca se conectam na rede, criando centenas de componentes isolados.

Essa fragmentação, embora seja uma descoberta metodológica válida que reflete a especialização dos esportes, **limita a aplicação de algoritmos de mineração de redes**, já que algoritmos como Louvain, PageRank e HITS funcionam melhor em redes conectadas. Em redes fragmentadas, Louvain basicamente detecta os componentes isolados como comunidades, o que não revela estrutura social subjacente.

## A Proposta: Rede Bipartida

A solução que estou propondo é modelar uma **rede bipartida**, que é conceitualmente mais natural para esse problema e resolve a fragmentação mantendo toda a riqueza da informação.

### Estrutura da Rede Bipartida

Uma rede bipartida possui **dois tipos de nós**:

1. **Nós Tipo 1 - Atletas**: Cada atleta é um nó (Phelps, Bolt, etc.)
2. **Nós Tipo 2 - Pódios**: Cada pódio olímpico é um nó identificado por (Ano, Evento, Sexo)

**Arestas** conectam atletas a pódios:
- Aresta existe se o atleta conquistou medalha naquele pódio
- Cada aresta tem **atributos**: tipo de medalha (Ouro/Prata/Bronze) e peso

### Ponderação Preservada

A ponderação é **mantida** através de atributos nas arestas:

- Aresta (Atleta → Pódio) com atributo `medal='Gold'` recebe peso **5**
- Aresta (Atleta → Pódio) com atributo `medal='Silver'` recebe peso **3**
- Aresta (Atleta → Pódio) com atributo `medal='Bronze'` recebe peso **2**

Essa ponderação reflete a **hierarquia de performance**: quanto melhor a medalha, maior o peso da conexão.

### Exemplo Concreto

```
Pódio: "2008_Swimming_100m_Butterfly_M"
   ↑ (Gold, peso=5)
Phelps ──────────────┐
                     │
Cavic ───────────────┤ (Silver, peso=3)
                     │
Milorad ─────────────┘ (Bronze, peso=2)
```

Esse mesmo atleta Phelps está conectado a múltiplos pódios:
- 2004_200m_Butterfly_M (Gold)
- 2008_100m_Butterfly_M (Gold)
- 2008_4x100m_Relay_M (Gold)
- etc.

### Por Que Essa Modelagem É Superior?

#### 1. **Zero Fragmentação**
- A rede é **única e conectada**
- Atletas de diferentes eventos estão conectados **indiretamente** através de pódios compartilhados
- Exemplo: Phelps (natação 100m) e Lochte (natação 200m) compartilham o pódio do revezamento 4x100m

#### 2. **Preserva Informação Temporal**
- Cada pódio tem timestamp (Year)
- Possibilita análise de evolução histórica
- Filtragem por décadas: "Quem dominou nos anos 2000?"

#### 3. **Conceitualmente Correta**
- Modela a realidade: atletas **participam** de pódios
- Não cria arestas artificiais entre atletas que nunca competiram juntos
- Não cria arestas fantasmas entre gerações diferentes

#### 4. **Flexibilidade Analítica**
Podemos fazer **duas análises complementares**:

**A) Análise Direta da Rede Bipartida**
- Métricas de atletas: quantos pódios? Quais tipos de medalhas?
- Métricas de pódios: quantos atletas únicos? Nível de competitividade?

**B) Projeção em Atletas** (Rede Unipartida Derivada)
- Projeta a rede bipartida em uma rede de atletas
- Dois atletas conectados se **compartilharam pódios**
- Peso da aresta = número de pódios compartilhados × peso da medalha
- Essa rede projetada é **densa e conectada**, ideal para mineração!

## Comportamento dos Algoritmos

Agora vou explicar como cada algoritmo que você está aplicando se comportará nessa modelagem:

### 1. PageRank

**Na rede bipartida:**
- PageRank flui entre atletas e pódios
- **Atleta com PageRank alto**: participou de muitos pódios importantes (pódios que também têm outros atletas importantes)
- **Pódio com PageRank alto**: teve atletas importantes competindo (pódios "de elite")

**Na rede projetada (atletas):**
- PageRank captura **influência através de co-ocorrências**
- Atleta influente = compartilhou pódios com muitos outros atletas influentes
- **Interpreta como**: versatilidade e presença em pódios disputados

**Responde à pergunta "maior atleta historicamente"?**
- **Parcialmente**. PageRank favorece atletas que:
  - Ganharam muitas medalhas (muitos pódios)
  - Competiram contra outros grandes atletas (pódios "importantes")
- Mas não distingue claramente entre ouro/prata/bronze sozinho
- **Solução**: usar PageRank **ponderado** pelos pesos das arestas

### 2. HITS (Hubs e Authorities)

HITS é **perfeito** para redes bipartidas!

**Na rede bipartida original:**
- **Authorities (Atletas)**: Atletas que participaram de muitos pódios importantes
  - **Alta Authority** = Phelps (muitos pódios, muitos ouros)
- **Hubs (Pódios)**: Pódios que tiveram muitos atletas importantes
  - **Alto Hub** = Pódios extremamente competitivos (finais com vários campeões)

**Interpretação:**
- **Authority Score** identifica os **atletas mais dominantes**
- **Hub Score** identifica os **pódios mais competitivos** (muitos campeões juntos)

**Responde "maior atleta historicamente"?**
- **SIM!** Authority score é uma excelente métrica para isso
- Atletas com muitos ouros em pódios competitivos terão Authority altíssimo

### 3. Centralidades (Degree, Betweenness, Closeness)

#### **Degree Centrality**

**Na rede bipartida:**
- **Degree de atleta** = número de pódios que participou
- Simples mas efetivo: quantifica **produtividade** de medalhas

**Na rede projetada:**
- **Degree de atleta** = número de atletas diferentes com quem compartilhou pódios
- Quantifica **amplitude de rivalidades**

#### **Betweenness Centrality**

**Na rede bipartida:**
- **Alta Betweenness** = atleta que conecta pódios de diferentes "comunidades"
- Exemplo: Atleta que compete em eventos individuais E revezamentos
- **Identifica atletas versáteis** que fazem "ponte" entre modalidades

**Na rede projetada:**
- Atleta que conecta diferentes "comunidades" de competidores
- Menos relevante para identificar "maior atleta", mais para identificar **conectores**

#### **Closeness Centrality**

**Na rede bipartida:**
- Distância média de um atleta para todos os pódios
- Menos interpretável nesse contexto

**Na rede projetada:**
- Atleta "próximo" de todos os outros através de pódios compartilhados
- Identifica atletas **centrais na comunidade olímpica**

### 4. Entropia de Shannon (Diversidade Temporal)

A entropia mede **diversidade** e **uniformidade** de distribuições.

**Aplicação 1: Diversidade de Medalhas de um Atleta**
```
H = -Σ p(medal) × log(p(medal))
```
- p(Gold) = proporção de ouros
- p(Silver) = proporção de pratas
- p(Bronze) = proporção de bronzes

**Interpretação:**
- **Entropia baixa**: Atleta consistente (ex: só ouros) → Phelps
- **Entropia alta**: Atleta com medalhas variadas

**Aplicação 2: Diversidade Temporal de um Pódio**
```
H = -Σ p(year) × log(p(year))
```
- Mede se um evento teve medalhistas distribuídos uniformemente ao longo dos anos
- **Entropia alta**: Evento sem domínio prolongado (muita renovação)
- **Entropia baixa**: Evento com domínio de poucos atletas ao longo do tempo

**Aplicação 3: Diversidade de Eventos de um Atleta**
- Mede **versatilidade**: atleta compete em quantos eventos diferentes?
- Alta entropia = generalista (compete em muitos eventos)
- Baixa entropia = especialista (foca em poucos eventos)

**Responde "maior atleta historicamente"?**
- **Não diretamente**, mas complementa
- Identifica **consistência** (baixa entropia de medalhas = sempre ouro)
- Identifica **versatilidade** (alta entropia de eventos = generalista)

### 5. Coeficiente de Gini (Desigualdade)

Gini mede **desigualdade** em distribuições (0 = igualdade perfeita, 1 = desigualdade máxima).

**Aplicação 1: Desigualdade de PageRank**
```
Gini(PageRank)
```
- Mede **concentração de influência**
- Gini alto = poucos atletas dominam (ex: Phelps com PageRank muito acima dos outros)
- Gini baixo = influência distribuída uniformemente

**Aplicação 2: Desigualdade de Medalhas por País**
```
Gini(medalhas por país)
```
- Mede concentração de medalhas em poucos países
- Alta desigualdade = USA, China dominam
- Baixa desigualdade = medalhas distribuídas

**Aplicação 3: Desigualdade de Pódios por Atleta**
- Mede se poucos atletas acumulam muitos pódios
- Identifica **concentração de domínio**

**Responde "maior atleta historicamente"?**
- **Não diretamente**, mas contextualiza
- Gini alto no esporte indica que há "super-atletas" dominantes
- Útil para comparar **nível de concentração** entre esportes

## Identificando o "Maior Atleta Historicamente"

Para responder essa pergunta, a rede bipartida permite **múltiplas métricas complementares**:

### **Métricas Diretas:**

1. **Total de Pódios (Degree)**: Quantos pódios participou?
2. **Total de Ouros**: Contagem ponderada de medalhas de ouro
3. **Score Ponderado**: `Gold×5 + Silver×3 + Bronze×2`

### **Métricas de Rede:**

4. **Authority Score (HITS)**: ⭐ **MELHOR MÉTRICA**
   - Captura domínio em pódios importantes
   - Favorece atletas com muitos ouros em finais competitivas

5. **PageRank Ponderado**:
   - Influência através de co-ocorrências ponderadas
   - Favorece versatilidade + consistência

6. **Betweenness (se alto)**:
   - Indica versatilidade entre modalidades
   - Complementar, não principal

### **Métricas de Consistência:**

7. **Entropia de Medalhas (baixa)**:
   - Consistência (sempre ouro)

8. **Gini de Medalhas ao Longo do Tempo**:
   - Concentração temporal de sucesso

### **Score Composto (Sugestão):**

```
Dominance Score =
  0.4 × Authority (HITS) +
  0.3 × PageRank Ponderado +
  0.2 × Score Ponderado de Medalhas +
  0.1 × (1 - Entropia de Medalhas)
```

Esse score combina:
- Importância estrutural (HITS, PageRank)
- Performance bruta (medalhas)
- Consistência (entropia baixa)

## Resumo Executivo

### **Vantagens da Rede Bipartida:**

✅ **Rede única e conectada** (zero fragmentação)
✅ **Preserva temporalidade** (cada pódio tem timestamp)
✅ **Mantém ponderação** (pesos por tipo de medalha)
✅ **Conceitualmente correta** (modela participação em pódios)
✅ **Flexível**: análise bipartida + projeção
✅ **Algoritmos funcionam bem**: HITS, PageRank, centralidades
✅ **Responde "maior atleta"**: através de Authority + métricas compostas

### **O Que Muda na Análise:**

1. **Detecção de Comunidades (Louvain)**:
   - Aplicado na **rede projetada** (atletas)
   - Detecta grupos de atletas que compartilham pódios frequentemente
   - Pode revelar "eras" (atletas da mesma geração) ou "estilos" (especialistas vs generalistas)

2. **PageRank**:
   - Na rede bipartida: flui entre atletas e pódios
   - Na rede projetada: captura influência por co-ocorrências

3. **HITS**:
   - **Authority = atletas dominantes**
   - **Hub = pódios competitivos**

4. **Entropia de Shannon**:
   - Diversidade de medalhas (consistência)
   - Diversidade temporal (domínio prolongado vs renovação)
   - Diversidade de eventos (versatilidade)

5. **Gini**:
   - Desigualdade de PageRank (concentração de influência)
   - Contextualiza o nível de domínio no esporte

## Implementação

A implementação é direta e usa estruturas já disponíveis. A mudança principal é na construção do grafo: ao invés de conectar atletas diretamente, conectamos atletas a pódios. Depois, podemos projetar em atletas quando necessário.

Essa modelagem resolve a fragmentação, mantém toda a informação, e permite aplicar todos os algoritmos planejados de forma significativa.

---

**Professora, o que você acha dessa abordagem? Faz sentido metodologicamente? Gostaria de discutir se há alguma limitação que eu não esteja enxergando.**

Fico no aguardo do seu retorno!

Abraços,
Caio
