# Dados Olímpicos - Dataset e Processamento

Este diretório contém os datasets olímpicos utilizados no TCC.

---

## 📊 Datasets Originais

### Dataset Histórico (1896-2016)

**Arquivo**: `athlete_events.csv` (36 MB)
**Fonte**: [120 years of Olympic history: athletes and results](https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results) (Kaggle)
**Autor**: Randi Griffin
**Período**: Atenas 1896 até Rio 2016
**Registros**: 271.116 participações
**Atletas únicos**: 135.334
**Colunas**: 15 (ID, Name, Sex, Age, Height, Weight, Team, NOC, Games, Year, Season, City, Sport, Event, Medal)

### Dataset Tokyo 2020

**Arquivo**: `tokyo2020_medals.csv`
**Fonte**: [Tokyo Olympics 2020 Medal Data](https://www.kaggle.com/datasets/piterfm/tokyo-2020-olympics)
**Autor**: piterfm
**Período**: Tokyo 2020 (realizado em 2021)
**Registros**: 2.411 participações medalhistas

### Dataset Consolidado

**Arquivo**: `athlete_events.csv` (atual)
**Descrição**: Integração dos dois datasets acima
**Período completo**: Atenas 1896 até Tokyo 2020 (1896-2021)
**Registros**: 273.527 participações (após remoção de duplicatas)
**Atletas únicos**: 137.745
**Modalidades esportivas**: 84
**Eventos distintos**: 1.063
**Comitês Olímpicos Nacionais**: 231
**Edições dos Jogos**: 52

---

## 🔄 Dataset Filtrado

### Processo de Filtragem

A partir do dataset consolidado, foi aplicado filtro para as 6 modalidades de interesse:

**Arquivo**: `athlete_events_cleaned.csv`
**Modalidades selecionadas**:
- Athletics (Atletismo)
- Swimming (Natação)
- Basketball (Basquete)
- Boxing (Boxe)
- Football (Futebol)
- Judo (Judô)

**Critérios de filtragem**:
- ✅ Apenas Jogos Olímpicos de Verão
- ✅ Apenas atletas medalhistas (medalhas de ouro, prata ou bronze)
- ✅ Apenas as 6 modalidades selecionadas

**Resultado**:
- **Registros**: 83.497 participações medalhistas
- **Atletas únicos**: 48.949 (todos os atletas nas 6 modalidades)
- **Medalhistas únicos**: 8.679 (atletas que conquistaram medalhas)

---

## 📈 Hierarquia dos Dados

| Nível | Descrição | Atletas Únicos | Arquivo |
|-------|-----------|----------------|---------|
| **Dataset completo** | Todos os atletas (1896-2020), todas as 84 modalidades | 137.745 | `athlete_events.csv` |
| **Dataset filtrado** | Atletas nas 6 modalidades selecionadas | 48.949 | `athlete_events_cleaned.csv` |
| **Medalhistas** | Atletas que conquistaram medalhas nas 6 modalidades | 8.679 | (filtrado do cleaned) |
| **149 redes** | Redes per-event (Year × Event × Gender) | 8.679 | `../results_per_event_cleaned/` |
| **12 casos de estudo** | Redes selecionadas via Iconic Score | 2.826 | (subconjunto das 149) |

### Detalhamento por Modalidade (Medalhistas)

| Modalidade | Atletas Medalhistas |
|------------|---------------------|
| Athletics | 3.026 |
| Swimming | 1.731 |
| Football | 1.568 |
| Basketball | 915 |
| Boxing | 912 |
| Judo | 528 |
| **TOTAL** | **8.679** |

---

## 📁 Arquivos Auxiliares

### Normalização de Eventos

**Arquivo**: `event_normalization_mapping.csv`
**Descrição**: Mapeamento para padronização de nomenclatura de eventos ao longo das diferentes edições olímpicas.

**Exemplo**:
- "Men's 100 metres" → "100m"
- "Women's Basketball" → "Basketball Women's Basketball"

---

## 🚀 Como Obter os Dados

### Opção 1: Download Manual (Recomendado)

1. Baixe o dataset histórico do Kaggle:
   ```bash
   # Link: https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results
   # Arquivo: athlete_events.csv
   ```

2. Baixe o dataset Tokyo 2020:
   ```bash
   # Link: https://www.kaggle.com/datasets/piterfm/tokyo-2020-olympics
   # Arquivo: medals.csv (renomear para tokyo2020_medals.csv)
   ```

3. Coloque os arquivos neste diretório (`main/data/`)

### Opção 2: Usar Arquivo Consolidado

Se você já tem o arquivo `athlete_events.csv` (273.527 registros), pode pular o passo 1 e 2 acima.

### Opção 3: Usar Apenas Dataset Filtrado

Se você quer apenas executar análises nos 6 esportes, basta ter o arquivo `athlete_events_cleaned.csv`.

---

## 📌 Notas Importantes

- ⚠️ Os arquivos `.csv` grandes (> 10 MB) não são commitados no Git (ver `.gitignore`)
- ✅ O arquivo `event_normalization_mapping.csv` é commitado (pequeno, essencial)
- ✅ O processamento de filtragem é reproduzível via scripts em `../src/data_processing/`
- 📊 As redes GEXF geradas estão em `../results_per_event_cleaned/`

---

## 🔧 Scripts de Processamento

Localização: `main/src/data_processing/`

1. **Consolidação dos datasets**: Integra dataset histórico + Tokyo 2020
2. **Normalização de eventos**: Aplica mapeamento de nomenclatura
3. **Filtragem por modalidades**: Gera `athlete_events_cleaned.csv`
4. **Geração de redes**: Cria 149 arquivos `.gexf` (per-event)

---

**Última atualização**: Fevereiro 2026
**Referência**: Ver Capítulo 3 (Desenvolvimento) da monografia para detalhes metodológicos
