# 🔧 REFATORAÇÃO DO DASHBOARD - PLANEJAMENTO

**Data:** 2026-02-05
**Status:** PLANEJAMENTO
**Objetivo:** Corrigir todos os problemas de filtros, dados e visualizações enviesadas

---

## 📋 ESTADO ATUAL (PROBLEMAS IDENTIFICADOS)

### ❌ CRÍTICO 1: Filtro de Eventos Inativo
- **Arquivo:** `main/src/dashboard/app.py` (linhas 168-196)
- **Problema:** Sidebar renderiza filtro de eventos, mas `data['metadata']` é sempre `None`
- **Causa:** `data_loader_wrapper.py` não carrega metadata em `load_all()`
- **Impacto:** Usuário não consegue selecionar eventos específicos

### ❌ CRÍTICO 2: Arquivo CSV Desatualizado
- **Arquivo Atual:** `consolidated_sports_network_analysis.csv` (9.350 atletas, 12 redes agregadas)
- **Arquivo Correto:** `consolidated_all_networks.csv` (19.103 atletas, 149 redes per-event)
- **Problema:** CSV antigo não tem coluna `network_id`, impossibilita filtro por evento
- **Impacto:** Dashboard usa dados antigos (12 casos) ao invés dos novos (149 redes)

### ❌ CRÍTICO 3: Tab Rivalidades Ignora Filtros
- **Arquivo:** `main/src/dashboard/app.py` (linhas 893-895)
- **Problema:**
  ```python
  def render_rivalries_tab(data):
      loader = DataLoader()  # ← IGNORA filtered_data passado como parâmetro
      rivalries = loader.load_rivalry_pairs(...)  # ← Carrega dados brutos de novo
  ```
- **Impacto:** Mostra rivalidades de TODOS os esportes, mesmo quando usuário filtra

### ❌ CRÍTICO 4: Tab Rede Interativa Ignora Filtros
- **Arquivo:** `main/src/dashboard/app.py` (linhas 1057-1087)
- **Problema:** Oferece apenas 16 redes hardcoded, não usa filtros da sidebar
- **Impacto:** Usuário não pode visualizar eventos específicos que selecionou

### ⚠️ IMPORTANTE 1: Comparações Cross-Esporte Enviesadas
- **Arquivos:** `app.py` (linhas 492, 540, 678, 1004)
- **Problema:** Visualizações agregam PageRank de esportes diferentes sem contexto
- **Exemplos:**
  - CDF de PageRank global
  - Scatter Size vs PageRank (comunidades de 3 vs 300 atletas)
  - Heatmap de Segregação cross-esporte
  - Rankings globais de PageRank
- **Impacto:** Viola lógica de per-event modeling, gera interpretações enviesadas

### ⚠️ IMPORTANTE 2: Falta Feedback Visual
- **Problema:** Usuário não vê quantas redes/atletas estão selecionados em cada tab
- **Impacto:** Dificuldade de entender o efeito dos filtros

---

## 🎯 ESTADO DESEJADO (OBJETIVOS)

### ✅ Princípio 1: Separação Rigorosa por Esporte
- **NÃO** comparar PageRank entre esportes diferentes
- **NÃO** normalizar PageRank (manter valores originais)
- **SIM** mostrar rankings/análises **por esporte e sexo separadamente**

### ✅ Princípio 2: Comparações Válidas M vs F
- **SIM** comparar Masculino vs Feminino **dentro do mesmo esporte**
- **Exemplo válido:** Swimming M vs Swimming F (densidade, modularidade, etc.)
- **Exemplo inválido:** Swimming M vs Football M (PageRank)

### ✅ Princípio 3: Filtros Funcionais
- Filtro de Esporte → funciona
- Filtro de Sexo → funciona
- **Filtro de Evento → deve funcionar!**
- Filtro Temporal → funciona

### ✅ Princípio 4: Todas as Tabs Respeitam Filtros
- Tab 1: Visão Geral ✓ (já respeita)
- Tab 2: Comunidades ✓ (já respeita)
- Tab 3: Atletas-Ponte ✓ (já respeita)
- **Tab 4: Rivalidades → corrigir para respeitar**
- Tab 5: Rankings ✓ (já respeita)
- Tab 6: Temporal ✓ (já respeita)
- **Tab 7: Rede Interativa → corrigir para respeitar**

### ✅ Princípio 5: Feedback Visual Claro
- Cada tab mostra: "📊 X atletas de Y redes selecionadas"
- Sidebar mostra: "Z redes disponíveis após filtros"

---

## 🛠️ PLANO DE REFATORAÇÃO

### FASE 1: INFRAESTRUTURA DE DADOS (30 min)

#### 1.1 Atualizar DataLoader para Carregar Dados Corretos

**Arquivo:** `main/src/core/data_loader_wrapper.py`

**Ação 1.1.1:** Adicionar método `load_network_metadata()`
```python
def load_network_metadata(self) -> pd.DataFrame:
    """
    Carrega metadata de todas as redes processadas.

    Returns:
        DataFrame com: network_id, sport, gender, event_name,
                      n_athletes, n_edges, density, etc.
    """
    path = PATHS.get('network_metadata')
    if path and path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()
```

**Ação 1.1.2:** Modificar `load_all()` para incluir metadata
```python
def load_all(self) -> Dict:
    data = {
        'athletes': self.load_consolidated_athletes(),
        'metadata': self.load_network_metadata(),  # ← NOVO
        'edges': self.load_consolidated_edges(),
        # ... resto dos dados
    }
    return data
```

**Ação 1.1.3:** Garantir que `load_consolidated_athletes()` carrega CSV correto
- Verificar se está carregando `consolidated_all_networks.csv` (149 redes)
- NÃO `consolidated_sports_network_analysis.csv` (12 casos antigos)

**Validação:**
```python
# Teste: carregar dados e verificar
loader = DataLoader()
data = loader.load_all()
assert 'metadata' in data
assert len(data['metadata']) == 149  # 149 redes
assert 'network_id' in data['athletes'].columns  # coluna existe
```

---

### FASE 2: CORREÇÃO DOS FILTROS (30 min)

#### 2.1 Ativar Filtro de Eventos na Sidebar

**Arquivo:** `main/src/dashboard/app.py` (linhas 168-196)

**Ação 2.1.1:** Remover fallback enganoso
```python
# ANTES:
else:
    selected_events = None
    st.sidebar.info("ℹ️ Filtro de eventos disponível após mineração completa")

# DEPOIS:
else:
    selected_events = []
    st.sidebar.warning("⚠️ Metadata não carregada. Contate desenvolvedor.")
```

**Ação 2.1.2:** Adicionar debug info (temporário)
```python
# Após linha 168, adicionar:
if 'metadata' not in data or data['metadata'] is None or data['metadata'].empty:
    st.sidebar.error(f"DEBUG: metadata={'metadata' in data}, "
                     f"is_none={data.get('metadata') is None}, "
                     f"is_empty={data.get('metadata', pd.DataFrame()).empty}")
```

**Validação:**
- Rodar dashboard
- Verificar que filtro de eventos mostra lista de eventos
- Selecionar alguns eventos
- Verificar que `filters['events']` contém valores corretos

#### 2.2 Garantir Aplicação Correta do Filtro de Eventos

**Arquivo:** `main/src/dashboard/app.py` (linhas 336-395, função `apply_filters()`)

**Ação 2.2.1:** Verificar lógica de filtro de eventos (linha 355-362)
```python
# VERIFICAR se este bloco está correto:
if filters['events'] is not None and 'metadata' in data and 'network_id' in df.columns:
    metadata = data['metadata']
    valid_network_ids = metadata[
        metadata['event_name'].isin(filters['events'])
    ]['network_id'].unique()
    df = df[df['network_id'].isin(valid_network_ids)]
```

**Ação 2.2.2:** Adicionar log de debug
```python
# Após filtro de eventos:
if filters['events']:
    print(f"DEBUG: Filtrado para {len(valid_network_ids)} network_ids")
    print(f"DEBUG: {len(df)} atletas após filtro de eventos")
```

**Validação:**
- Selecionar 1 evento específico
- Verificar que apenas atletas daquele evento aparecem
- Verificar logs no terminal

---

### FASE 3: CORREÇÃO DAS TABS PROBLEMÁTICAS (1h)

#### 3.1 Tab 4: Rivalidades

**Arquivo:** `main/src/dashboard/app.py` (linhas 866-938)

**Ação 3.1.1:** Remover carregamento redundante
```python
# ANTES (linha 893-895):
def render_rivalries_tab(data):
    loader = DataLoader()
    rivalries_filtered = loader.load_rivalry_pairs(event_type=event_type)

# DEPOIS:
def render_rivalries_tab(filtered_data):
    # Usar filtered_data['rivalries'] diretamente
    rivalries = filtered_data.get('rivalries', pd.DataFrame())
```

**Ação 3.1.2:** Remover seletor de event_type (linha 887-891)
- Já está filtrado globalmente
- Não precisa de seletor local

**Ação 3.1.3:** Atualizar visualizações (linhas 920-938)
```python
# Usar filtered_data em vez de data global:
fig1 = barplot_top_rivalries(filtered_data['rivalries'], top_n=10)
fig2 = heatmap_segregation(filtered_data['connectivity'])
```

**Validação:**
- Selecionar apenas "Swimming M"
- Tab Rivalidades deve mostrar APENAS rivalidades de Swimming M
- Não deve aparecer Basketball, Football, etc.

#### 3.2 Tab 7: Rede Interativa

**Arquivo:** `main/src/dashboard/app.py` (linhas 1039-1450)

**Ação 3.2.1:** Remover lista hardcoded de 16 redes (linhas 1057-1087)

**Ação 3.2.2:** Gerar lista dinâmica baseada em filtros
```python
def render_network_tab(filtered_data):
    # Obter redes disponíveis após filtros
    metadata = filtered_data.get('metadata', pd.DataFrame())

    if metadata.empty:
        st.warning("Nenhuma rede disponível com os filtros selecionados")
        return

    # Criar lista de redes disponíveis
    network_options = []
    for _, row in metadata.iterrows():
        label = f"{row['sport'].title()} {row['gender']} - {row['event_name']}"
        network_options.append({
            'network_id': row['network_id'],
            'label': label,
            'sport': row['sport'],
            'gender': row['gender'],
            'event': row['event_name']
        })

    # Seletor de rede
    selected_label = st.selectbox("Selecione a rede:", [n['label'] for n in network_options])
    selected_network = next(n for n in network_options if n['label'] == selected_label)
```

**Ação 3.2.3:** Carregar rede selecionada dinamicamente
```python
# Substituir loader.load_sport_network() por:
network_id = selected_network['network_id']
network_athletes = filtered_data['athletes'][
    filtered_data['athletes']['network_id'] == network_id
]
```

**Validação:**
- Selecionar "Swimming M" nos filtros
- Tab Rede deve mostrar APENAS eventos de Swimming M
- Selecionar um evento específico
- Visualização deve carregar corretamente

---

### FASE 4: REMOVER VISUALIZAÇÕES ENVIESADAS (1h)

#### 4.1 CDF de PageRank (Global)

**Arquivo:** `main/src/dashboard/app.py` (linha 492)

**Opção A: REMOVER completamente**
```python
# Deletar linhas 492-499
# with col2:
#     st.markdown("**CDF de PageRank**")
#     fig = cdf_pagerank(data['athletes'], interactive=True)
#     st.plotly_chart(fig, use_container_width=True)
```

**Opção B: SUBSTITUIR por CDF por Esporte**
```python
with col2:
    st.markdown("**CDF de PageRank por Esporte**")

    # Separar por esporte
    for sport in filtered_data['athletes']['sport'].unique():
        sport_data = filtered_data['athletes'][
            filtered_data['athletes']['sport'] == sport
        ]
        fig = cdf_pagerank(sport_data, title=f"CDF PageRank - {sport.title()}")
        st.plotly_chart(fig, use_container_width=True)
```

**Decisão:** Opção A (remover). CDF cross-esporte é sempre enviesado.

#### 4.2 Scatter Size vs PageRank

**Arquivo:** `main/src/dashboard/app.py` (linha 540)

**Ação 4.2.1:** Adicionar aviso de limitação
```python
st.markdown("**Tamanho vs PageRank por Comunidade**")

# ADICIONAR:
st.info("⚠️ **Atenção:** PageRank é específico a cada rede. "
        "Comunidades de esportes diferentes não são diretamente comparáveis.")

fig = scatter_size_vs_pagerank(filtered_data['hierarchy'], interactive=True)
st.plotly_chart(fig, use_container_width=True)
```

**Ação 4.2.2:** Colorir por esporte (se múltiplos selecionados)
- Modificar `plots.py` para aceitar parâmetro `color_by='sport'`

#### 4.3 Rankings Globais de PageRank

**Arquivo:** `main/src/dashboard/app.py` (linhas 1004-1006)

**Ação 4.3.1:** REMOVER ranking global único

**Ação 4.3.2:** SUBSTITUIR por rankings por esporte
```python
# ANTES:
fig = table_top_athletes(
    filtered_data['athletes'],
    metric_column='original_pagerank',
    top_n=top_n
)

# DEPOIS:
st.markdown("### Rankings por Esporte")
st.info("📊 PageRank é calculado independentemente para cada rede. "
        "Rankings são apresentados por esporte para evitar comparações enviesadas.")

# Separar por esporte
for sport in sorted(filtered_data['athletes']['sport'].unique()):
    with st.expander(f"🏅 {sport.title()}", expanded=False):
        sport_data = filtered_data['athletes'][
            filtered_data['athletes']['sport'] == sport
        ]

        # Separar M e F
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Masculino**")
            m_data = sport_data[sport_data['gender'] == 'M']
            if not m_data.empty:
                fig_m = table_top_athletes(m_data, metric_column='pagerank', top_n=10)
                st.plotly_chart(fig_m, use_container_width=True)
            else:
                st.info("Sem dados")

        with col2:
            st.markdown("**Feminino**")
            f_data = sport_data[sport_data['gender'] == 'F']
            if not f_data.empty:
                fig_f = table_top_athletes(f_data, metric_column='pagerank', top_n=10)
                st.plotly_chart(fig_f, use_container_width=True)
            else:
                st.info("Sem dados")
```

**Validação:**
- Verificar que rankings aparecem separados por esporte
- Verificar que M e F estão lado a lado para comparação
- Verificar aviso sobre não-comparabilidade

#### 4.4 Heatmap de Segregação Cross-Esporte

**Arquivo:** `main/src/dashboard/app.py` (linha 678)

**Ação 4.4.1:** Verificar se `connectivity` já está filtrado
- Se sim, não precisa mudar nada
- Se não, aplicar filtro localmente

**Ação 4.4.2:** Adicionar aviso se múltiplos esportes selecionados
```python
if filtered_data['athletes']['sport'].nunique() > 1:
    st.warning("⚠️ Múltiplos esportes selecionados. "
               "Segregação é mais significativa dentro de cada esporte.")
```

---

### FASE 5: ADICIONAR FEEDBACK VISUAL (30 min)

#### 5.1 Informação de Seleção na Sidebar

**Arquivo:** `main/src/dashboard/app.py` (após linha 265)

**Ação 5.1.1:** Adicionar métricas após filtros
```python
# Após return de render_sidebar(), adicionar:
st.sidebar.markdown("---")
st.sidebar.subheader("Seleção Atual")

# Calcular estatísticas dos filtros
n_networks = filtered_data['metadata']['network_id'].nunique() if 'metadata' in filtered_data else 0
n_athletes = len(filtered_data['athletes'])
n_sports = filtered_data['athletes']['sport'].nunique()

col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric("Redes", n_networks)
    st.metric("Atletas", f"{n_athletes:,}")
with col2:
    st.metric("Esportes", n_sports)
    st.metric("Eventos", len(filters.get('events', [])))
```

#### 5.2 Informação em Cada Tab

**Arquivo:** `main/src/dashboard/app.py` (início de cada função render_*_tab())

**Ação 5.2.1:** Adicionar header padrão em todas as tabs
```python
def render_overview_tab(filtered_data):
    # ADICIONAR no início:
    st.info(f"📊 Analisando **{len(filtered_data['athletes']):,} atletas** "
            f"de **{filtered_data['metadata']['network_id'].nunique()} redes** selecionadas")

    # ... resto da tab
```

**Aplicar em:**
- render_overview_tab (linha 420)
- render_communities_tab (linha 572)
- render_bridges_tab (linha 740)
- render_rivalries_tab (linha 866)
- render_rankings_tab (linha 945)
- render_temporal_tab (linha 950)
- render_network_tab (linha 1039)

---

### FASE 6: TESTES E VALIDAÇÃO (30 min)

#### 6.1 Checklist de Testes Funcionais

```
TESTES DE FILTROS:
[ ] Filtro Esporte: selecionar "Swimming" → apenas Swimming aparece
[ ] Filtro Sexo: selecionar "M" → apenas Masculino aparece
[ ] Filtro Evento: selecionar 1 evento → apenas aquele evento aparece
[ ] Filtro Temporal: selecionar 1900-1950 → apenas atletas desse período
[ ] Combinação: Swimming + M + 100m Freestyle → resultado correto

TESTES POR TAB:
[ ] Tab 1 (Visão Geral): respeita filtros
[ ] Tab 2 (Comunidades): respeita filtros
[ ] Tab 3 (Atletas-Ponte): respeita filtros
[ ] Tab 4 (Rivalidades): respeita filtros (CORRIGIDO)
[ ] Tab 5 (Rankings): respeita filtros, sem cross-esporte
[ ] Tab 6 (Temporal): respeita filtros
[ ] Tab 7 (Rede Interativa): respeita filtros (CORRIGIDO)

TESTES DE VIÉS:
[ ] Nenhuma visualização compara PageRank cross-esporte
[ ] Rankings aparecem por esporte separadamente
[ ] Avisos de limitação aparecem onde necessário
[ ] CDF global removido

TESTES DE USABILIDADE:
[ ] Usuário vê quantas redes estão selecionadas
[ ] Usuário vê quantos atletas estão selecionados
[ ] Filtro de eventos funciona e mostra opções
[ ] Feedback visual claro em todas as tabs
```

#### 6.2 Teste de Carga

```python
# Script de teste:
# main/src/dashboard/test_dashboard.py

import sys
sys.path.insert(0, 'main/src')

from core.data_loader_wrapper import DataLoader

def test_load_all():
    loader = DataLoader()
    data = loader.load_all()

    # Verificações
    assert 'athletes' in data, "athletes não carregado"
    assert 'metadata' in data, "metadata não carregado"
    assert not data['metadata'].empty, "metadata vazio"
    assert 'network_id' in data['athletes'].columns, "network_id ausente"

    print(f"✓ {len(data['athletes']):,} atletas carregados")
    print(f"✓ {len(data['metadata'])} redes carregadas")
    print(f"✓ network_id presente: {data['athletes']['network_id'].nunique()} valores únicos")

if __name__ == '__main__':
    test_load_all()
```

**Executar:**
```bash
python main/src/dashboard/test_dashboard.py
```

#### 6.3 Teste Visual

**Cenário 1: Selecionar apenas Swimming Masculino**
1. Abrir dashboard
2. Filtros: Sport=Swimming, Sex=M
3. Verificar todas as 7 tabs
4. Confirmar que APENAS Swimming M aparece

**Cenário 2: Selecionar evento específico**
1. Filtros: Sport=Swimming, Sex=M, Event=100m Freestyle
2. Tab 7 (Rede): deve mostrar apenas aquele evento
3. Tab 5 (Rankings): deve mostrar apenas atletas daquele evento

**Cenário 3: Múltiplos esportes**
1. Filtros: Sport=Swimming+Athletics, Sex=M+F
2. Tab 5 (Rankings): deve mostrar rankings SEPARADOS por esporte
3. Nenhum ranking global cross-esporte deve aparecer

---

## 📦 ARQUIVOS QUE SERÃO MODIFICADOS

```
MODIFICAÇÕES:
✏️ main/src/core/data_loader_wrapper.py
   - Adicionar load_network_metadata()
   - Atualizar load_all()
   - Garantir carregamento de consolidated_all_networks.csv

✏️ main/src/dashboard/app.py
   - Corrigir render_sidebar() (filtro de eventos)
   - Corrigir apply_filters() (aplicação correta)
   - Refatorar render_rivalries_tab() (remover carregamento redundante)
   - Refatorar render_network_tab() (remover hardcoded, usar filtros)
   - Modificar render_rankings_tab() (separar por esporte)
   - Adicionar avisos em visualizações problemáticas
   - Adicionar feedback visual em todas as tabs
   - Remover CDF global

NOVOS ARQUIVOS:
📄 main/src/dashboard/test_dashboard.py
   - Script de validação

📄 main/docs/REFATORACAO_DASHBOARD_PLANEJAMENTO.md
   - Este documento
```

---

## ⏱️ ESTIMATIVA DE TEMPO

| Fase | Descrição | Tempo Estimado |
|------|-----------|----------------|
| Fase 1 | Infraestrutura de Dados | 30 min |
| Fase 2 | Correção dos Filtros | 30 min |
| Fase 3 | Correção das Tabs | 1h |
| Fase 4 | Remover Visualizações Enviesadas | 1h |
| Fase 5 | Adicionar Feedback Visual | 30 min |
| Fase 6 | Testes e Validação | 30 min |
| **TOTAL** | | **3h 30min** |

---

## 🎯 CRITÉRIOS DE SUCESSO

**Ao final da refatoração, o dashboard deve:**

✅ Carregar dados corretos (149 redes, 19.103 atletas)
✅ Filtro de eventos funcional e ativo
✅ TODAS as 7 tabs respeitam TODOS os filtros
✅ ZERO comparações cross-esporte de PageRank
✅ Rankings separados por esporte (M e F lado a lado)
✅ Feedback visual claro em cada tab
✅ Usuário entende quantas redes/atletas estão selecionados
✅ Avisos de limitação onde necessário
✅ Testes funcionais passam 100%

---

## 📝 NOTAS IMPORTANTES

### Sobre Comparações Válidas:
- ✅ **VÁLIDO:** Swimming M vs Swimming F (densidade, modularidade)
- ✅ **VÁLIDO:** Top 10 PageRank em Swimming M (intra-rede)
- ❌ **INVÁLIDO:** Swimming M vs Football M (PageRank)
- ❌ **INVÁLIDO:** Top 20 Global PageRank (cross-esporte)

### Sobre Normalização:
- **NÃO normalizar PageRank** - manter valores originais por rede
- Valores já são contextualizados por esporte/sexo
- Comparações só dentro do mesmo contexto

### Sobre Filtros:
- Esporte + Sexo + Evento = contexto completo
- Filtro de evento permite análise granular (per-event)
- Todas as visualizações devem respeitar contexto selecionado

---

**PRÓXIMOS PASSOS:**
1. ✅ Revisar este documento
2. ⏳ Executar Fase 1 (Infraestrutura)
3. ⏳ Executar Fase 2 (Filtros)
4. ⏳ Executar Fase 3 (Tabs)
5. ⏳ Executar Fase 4 (Visualizações)
6. ⏳ Executar Fase 5 (Feedback)
7. ⏳ Executar Fase 6 (Testes)
8. ⏳ Commit das mudanças

---

**Status:** 🟡 AGUARDANDO APROVAÇÃO PARA INICIAR
