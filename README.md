# 📊 Dashboard de Monitoramento de Ativos Industriais

> Sprint 2 — Visualização Operacional com Streamlit

## ✅ O que está implementado

| Requisito | Status |
|---|---|
| Navegação por Planta/Área | ✅ Sidebar com selectbox |
| Dashboard de Telemetria/Sensor | ✅ KPIs com st.metric |
| Gráficos Temporais (Séries Temporais) | ✅ Plotly com hover interativo |
| Alertas e Status (Verde/Amarelo/Vermelho) | ✅ Indicadores visuais + linhas de limite |
| Integração de Cadastro Visual | ✅ Placa de identificação + histórico |
| Persistência com @st.cache_data | ✅ Implementado |

---

## 🚀 Como Rodar

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Iniciar o dashboard
streamlit run app.py
```

O dashboard abre automaticamente em: **http://localhost:8501**

---

## 🔄 Como Integrar Seus Dados Reais (Sprint 1)

### Opção A — Arquivo CSV

Localize a função `carregar_dados_historicos()` em `app.py` e substitua o corpo por:

```python
@st.cache_data(ttl=30)
def carregar_dados_historicos(tag: str, _status: str) -> pd.DataFrame:
    df = pd.read_csv(f"dados/{tag}.csv", parse_dates=["timestamp"])
    # Garanta que as colunas se chamam: timestamp, temperatura, vibracao
    return df
```

### Opção B — Banco de Dados SQL (PostgreSQL/MySQL/SQLite)

```python
import sqlalchemy as sa

@st.cache_data(ttl=30)
def carregar_dados_historicos(tag: str, _status: str) -> pd.DataFrame:
    engine = sa.create_engine("postgresql://usuario:senha@host:5432/banco")
    query = f"""
        SELECT timestamp, temperatura, vibracao
        FROM telemetria
        WHERE tag = '{tag}'
          AND timestamp >= NOW() - INTERVAL '48 hours'
        ORDER BY timestamp ASC
    """
    return pd.read_sql(query, engine, parse_dates=["timestamp"])
```

### Opção C — Imagem da Placa via Visão Computacional

Na aba **Identificação Visual**, substitua o placeholder por:

```python
# Imagem local:
st.image("assets/placas/MT-001.jpg", caption="Placa — MT-001")

# Ou base64 extraída via OCR/CV na Sprint 1:
# st.image(decoded_image_bytes, caption=f"Placa — {tag}")
```

---

## 📁 Estrutura do Projeto

```
dashboard_motores/
├── app.py              # Aplicação principal Streamlit
├── requirements.txt    # Dependências Python
├── README.md           # Este arquivo
└── assets/             # (Crie esta pasta)
    └── placas/         # Imagens das placas por TAG (ex: MT-001.jpg)
```

---

## 🎨 Arquitetura do Dashboard

```
┌─────────────────────────────────────────────────┐
│                   TOPBAR                        │
├───────────┬─────────────────────────────────────┤
│           │  KPIs: Temperatura | Vibração | ... │
│ SIDEBAR   ├─────────────────────────────────────┤
│           │  TABS:                              │
│ - Planta  │  [Telemetria] [Alarmes] [Ident.]   │
│ - TAG     │                                     │
│           │  Gráficos Plotly (hover interativo) │
│           │  Séries temporais + limite visual   │
└───────────┴─────────────────────────────────────┘
```

---

## ⚙️ Limites Operacionais

Ajuste o dicionário `LIMITES` em `app.py`:

```python
LIMITES = {
    "temp": 60.0,        # °C — temperatura crítica
    "vib": 4.5,          # mm/s — vibração crítica
    "corrente_max": 50.0 # A — corrente máxima
}
```

---

## 📦 Deploy

```bash
# Streamlit Cloud (gratuito)
# 1. Suba o repositório para o GitHub
# 2. Acesse: https://share.streamlit.io
# 3. Conecte o repo e selecione app.py

# Docker
docker build -t dashboard-motores .
docker run -p 8501:8501 dashboard-motores
```
