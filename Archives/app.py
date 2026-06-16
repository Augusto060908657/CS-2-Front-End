"""
Dashboard de Monitoramento de Ativos Industriais
================================================
Sprint 2 — Visualização Operacional

SUBSTITUA os dados simulados pelos seus dados reais:
- Função `carregar_dados_reais(tag)` → conecte ao seu CSV/SQL da Sprint 1
- Dicionário `MOTOR_DB` → carregue do seu cadastro de ativos
- Variável `LIMITES` → ajuste conforme especificação técnica de cada ativo

Dependências: pip install streamlit pandas plotly
Para rodar:   streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import time

# ─────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    layout="wide",
    page_title="SCADA — Monitoramento de Motores",
    page_icon="⚙️",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CSS PERSONALIZADO (Tema Industrial Escuro)
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Fundo geral */
    .stApp { background-color: #0F1117; color: #F0F4FF; }
    .main .block-container { padding: 1rem 1.5rem; max-width: 100%; }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #161923; border-right: 1px solid #252A3D; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: #8B9AC0 !important; }

    /* Métricas */
    [data-testid="stMetric"] {
        background: #1E2233; border: 1px solid #252A3D;
        border-radius: 8px; padding: 14px 16px;
    }
    [data-testid="stMetricLabel"] { color: #4B5780 !important; font-size: 11px !important; }
    [data-testid="stMetricValue"] { color: #F0F4FF !important; }
    [data-testid="stMetricDelta"] { font-size: 12px !important; }

    /* Títulos */
    h1, h2, h3 { color: #F0F4FF !important; }

    /* Abas */
    .stTabs [data-baseweb="tab-list"] { background: #161923; gap: 4px; }
    .stTabs [data-baseweb="tab"] { background: #161923; color: #8B9AC0; border: none; }
    .stTabs [aria-selected="true"] { background: #1E2233 !important; color: #60A5FA !important; }

    /* Badge de simulação */
    .sim-badge {
        background: rgba(59,130,246,0.15); color: #60A5FA;
        padding: 4px 12px; border-radius: 20px; font-size: 12px;
        border: 1px solid rgba(59,130,246,0.3); display: inline-block;
    }

    /* Placa de identificação */
    .id-plate {
        background: #252A3D; border-radius: 8px; padding: 16px;
        font-family: 'Courier New', monospace; font-size: 13px;
        border: 1px solid #3B4260; line-height: 2;
    }

    /* Alarme */
    .alarme-crit {
        background: rgba(239,68,68,0.1); border-left: 3px solid #EF4444;
        border-radius: 6px; padding: 10px 14px; margin-bottom: 8px;
        font-size: 13px; color: #F0F4FF;
    }
    .alarme-warn {
        background: rgba(245,158,11,0.1); border-left: 3px solid #F59E0B;
        border-radius: 6px; padding: 10px 14px; margin-bottom: 8px;
        font-size: 13px; color: #F0F4FF;
    }
    .alarme-info {
        background: rgba(34,197,94,0.1); border-left: 3px solid #22C55E;
        border-radius: 6px; padding: 10px 14px; margin-bottom: 8px;
        font-size: 13px; color: #F0F4FF;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# BANCO DE DADOS DE ATIVOS (SIMULADO)
# ─── SUBSTITUA PELA SUA FONTE DE DADOS ────
# ─────────────────────────────────────────────
MOTOR_DB = {
    "Planta A — Linha 1": {
        "MT-001": {
            "nome": "Motor Ventilação Principal",
            "modelo": "WEG W22 90L",
            "potencia": "7,5 kW",
            "tensao": "380 V",
            "ip": "IP55",
            "serie": "WE22-2026-001",
            "instalacao": "Jan/2023",
            "temp_atual": 48.0,
            "vib_atual": 1.8,
            "corrente": 32.1,
            "rpm": 1450,
            "status": "ok",
        },
        "MT-002": {
            "nome": "Motor Bomba Hidráulica",
            "modelo": "WEG W22 100L",
            "potencia": "11 kW",
            "tensao": "380 V",
            "ip": "IP55",
            "serie": "WE22-2025-042",
            "instalacao": "Mar/2022",
            "temp_atual": 58.0,
            "vib_atual": 3.9,
            "corrente": 38.4,
            "rpm": 1430,
            "status": "warn",
        },
        "MT-003": {
            "nome": "Motor Esteira Carga",
            "modelo": "WEG W22 80L",
            "potencia": "5,5 kW",
            "tensao": "220 V",
            "ip": "IP54",
            "serie": "WE22-2024-118",
            "instalacao": "Jul/2024",
            "temp_atual": 44.0,
            "vib_atual": 1.2,
            "corrente": 28.7,
            "rpm": 1455,
            "status": "ok",
        },
    },
    "Planta B — Linha 2": {
        "MT-004": {
            "nome": "Motor Compressor #1",
            "modelo": "Siemens 1LE1",
            "potencia": "15 kW",
            "tensao": "380 V",
            "ip": "IP65",
            "serie": "SI-1LE-2023-009",
            "instalacao": "Set/2021",
            "temp_atual": 71.0,
            "vib_atual": 5.8,
            "corrente": 52.0,
            "rpm": 1390,
            "status": "crit",
        },
        "MT-005": {
            "nome": "Motor Bomba Retorno",
            "modelo": "WEG W22 90L",
            "potencia": "7,5 kW",
            "tensao": "380 V",
            "ip": "IP55",
            "serie": "WE22-2026-077",
            "instalacao": "Nov/2023",
            "temp_atual": 46.0,
            "vib_atual": 2.1,
            "corrente": 29.5,
            "rpm": 1448,
            "status": "ok",
        },
    },
}

# Limites operacionais (°C e mm/s)
LIMITES = {"temp": 60.0, "vib": 4.5, "corrente_max": 50.0}

# ─────────────────────────────────────────────
# GERAÇÃO DE DADOS HISTÓRICOS SIMULADOS
# ─── SUBSTITUA POR: pd.read_csv() ou query SQL
# ─────────────────────────────────────────────
@st.cache_data(ttl=30)
def carregar_dados_historicos(tag: str, status: str) -> pd.DataFrame:
    """
    Gera dados históricos simulados com padrão de falha progressiva.

    COMO SUBSTITUIR:
        # Opção 1 — CSV da Sprint 1:
        df = pd.read_csv(f"dados/{tag}.csv", parse_dates=["timestamp"])
        return df

        # Opção 2 — Banco SQL:
        import sqlalchemy as sa
        engine = sa.create_engine("postgresql://user:pass@host/db")
        query = f"SELECT * FROM telemetria WHERE tag='{tag}' ORDER BY ts DESC LIMIT 500"
        return pd.read_sql(query, engine, parse_dates=["ts"])
    """
    np.random.seed(hash(tag) % 2**31)
    agora = datetime.now()
    periodos = 96  # 48h com leituras a cada 30 min
    timestamps = [agora - timedelta(minutes=30 * i) for i in range(periodos - 1, -1, -1)]

    base_temp = {"ok": 48, "warn": 56, "crit": 65}[status]
    base_vib = {"ok": 1.8, "warn": 3.5, "crit": 5.2}[status]

    temp_vals, vib_vals = [], []
    for i in range(periodos):
        prog = i / periodos
        ruido_t = np.random.normal(0, 0.8)
        ruido_v = np.random.normal(0, 0.15)
        if status == "crit":
            t = base_temp * (0.70 + prog * 0.30) + np.sin(i * 0.3) * 2 + ruido_t
            v = base_vib * (0.75 + prog * 0.25) + np.sin(i * 0.5) * 0.3 + ruido_v
        elif status == "warn":
            t = base_temp * (0.85 + prog * 0.15) + np.sin(i * 0.4) * 1.5 + ruido_t
            v = base_vib * (0.80 + prog * 0.20) + np.sin(i * 0.6) * 0.2 + ruido_v
        else:
            t = base_temp + np.sin(i * 0.25) * 3 + ruido_t
            v = base_vib + np.sin(i * 0.4) * 0.3 + ruido_v
        temp_vals.append(round(t, 2))
        vib_vals.append(round(max(v, 0.1), 2))

    return pd.DataFrame({"timestamp": timestamps, "temperatura": temp_vals, "vibracao": vib_vals})


# ─────────────────────────────────────────────
# HELPERS DE STATUS
# ─────────────────────────────────────────────
def get_status(info: dict) -> tuple[str, str]:
    """Retorna (label, emoji) baseado nos valores atuais."""
    if info["temp_atual"] > LIMITES["temp"] or info["vib_atual"] > LIMITES["vib"]:
        return "🔴 Crítico", "crit"
    if info["temp_atual"] > LIMITES["temp"] * 0.9 or info["vib_atual"] > LIMITES["vib"] * 0.8:
        return "🟡 Atenção", "warn"
    return "🟢 Saudável", "ok"


def cor_valor(valor: float, limite: float) -> str:
    """Cor semântica para exibição de métricas."""
    if valor > limite:
        return "🔴"
    if valor > limite * 0.9:
        return "🟡"
    return "🟢"


# ─────────────────────────────────────────────
# SIDEBAR — NAVEGAÇÃO
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Controle Operacional")
    st.markdown('<span class="sim-badge">⚠ Dados Simulados</span>', unsafe_allow_html=True)
    st.divider()

    planta = st.selectbox("🏭 Planta / Área", list(MOTOR_DB.keys()))
    motores_da_planta = MOTOR_DB[planta]

    # Renderiza lista de motores com indicadores de status
    st.markdown("**Motores disponíveis:**")
    motor_options = {}
    for tag, info in motores_da_planta.items():
        label, _ = get_status(info)
        emoji = label.split()[0]
        motor_options[f"{emoji}  {tag} — {info['nome']}"] = tag

    motor_label = st.radio("Selecione o motor (TAG):", list(motor_options.keys()), label_visibility="collapsed")
    tag = motor_options[motor_label]
    info = motores_da_planta[tag]

    st.divider()
    status_label, status_tipo = get_status(info)
    st.metric("Status Geral", status_label)
    st.caption(f"Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    if st.button("🔄 Atualizar Dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ─────────────────────────────────────────────
# CABEÇALHO PRINCIPAL
# ─────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title(f"📊 {tag} — {info['nome']}")
    st.caption(f"{planta}  •  {info['modelo']}  •  {info['potencia']}")
with col_h2:
    st.markdown(f"<br>", unsafe_allow_html=True)
    if status_tipo == "crit":
        st.error(f"{status_label}")
    elif status_tipo == "warn":
        st.warning(f"{status_label}")
    else:
        st.success(f"{status_label}")

# ─────────────────────────────────────────────
# KPIs — LINHA DE INDICADORES
# ─────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)

delta_temp = round(info["temp_atual"] - LIMITES["temp"], 1)
delta_vib = round(info["vib_atual"] - LIMITES["vib"], 2)

c1.metric(
    "🌡 Temperatura",
    f"{info['temp_atual']} °C",
    delta=f"{delta_temp:+.1f}°C vs limite",
    delta_color="inverse"
)
c2.metric(
    "📳 Vibração",
    f"{info['vib_atual']} mm/s",
    delta=f"{delta_vib:+.2f} vs limite",
    delta_color="inverse"
)
c3.metric("⚡ Corrente", f"{info['corrente']} A")
c4.metric("🔄 Velocidade", f"{info['rpm']} RPM")
c5.metric("🏷 TAG", tag)

st.divider()

# ─────────────────────────────────────────────
# ABAS PRINCIPAIS
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📈 Telemetria Histórica", "🚨 Alarmes e Eventos", "🔍 Identificação Visual"])

df = carregar_dados_historicos(tag, info["status"])

# ── TAB 1: GRÁFICOS DE SÉRIES TEMPORAIS ──
with tab1:
    col_g1, col_g2 = st.columns(2)

    # Gráfico de Temperatura
    with col_g1:
        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(
            x=df["timestamp"], y=df["temperatura"],
            mode="lines", name="Temperatura (°C)",
            line=dict(color="#3B82F6", width=2),
            fill="tozeroy", fillcolor="rgba(59,130,246,0.08)",
            hovertemplate="%{x|%d/%m %H:%M}<br><b>%{y:.1f} °C</b><extra></extra>"
        ))
        fig_temp.add_hline(
            y=LIMITES["temp"], line_dash="dash",
            line_color="#F59E0B", line_width=1.5,
            annotation_text=f"Limite: {LIMITES['temp']}°C",
            annotation_font_color="#F59E0B"
        )
        fig_temp.add_hline(
            y=LIMITES["temp"] * 0.9, line_dash="dot",
            line_color="#F59E0B", line_width=1, opacity=0.5,
            annotation_text="Alerta (90%)",
            annotation_font_color="#F59E0B"
        )
        fig_temp.update_layout(
            title="Temperatura (°C) — Últimas 48h",
            paper_bgcolor="#1E2233", plot_bgcolor="#1E2233",
            font=dict(color="#8B9AC0", size=12),
            xaxis=dict(gridcolor="#252A3D", showgrid=True),
            yaxis=dict(gridcolor="#252A3D", showgrid=True),
            showlegend=False, height=320,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig_temp, use_container_width=True)

    # Gráfico de Vibração
    with col_g2:
        fig_vib = go.Figure()
        fig_vib.add_trace(go.Scatter(
            x=df["timestamp"], y=df["vibracao"],
            mode="lines", name="Vibração (mm/s)",
            line=dict(color="#22C55E", width=2),
            fill="tozeroy", fillcolor="rgba(34,197,94,0.07)",
            hovertemplate="%{x|%d/%m %H:%M}<br><b>%{y:.2f} mm/s</b><extra></extra>"
        ))
        fig_vib.add_hline(
            y=LIMITES["vib"], line_dash="dash",
            line_color="#F59E0B", line_width=1.5,
            annotation_text=f"Limite: {LIMITES['vib']} mm/s",
            annotation_font_color="#F59E0B"
        )
        fig_vib.update_layout(
            title="Vibração (mm/s) — Últimas 48h",
            paper_bgcolor="#1E2233", plot_bgcolor="#1E2233",
            font=dict(color="#8B9AC0", size=12),
            xaxis=dict(gridcolor="#252A3D", showgrid=True),
            yaxis=dict(gridcolor="#252A3D", showgrid=True),
            showlegend=False, height=320,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig_vib, use_container_width=True)

    # Gráfico combinado — linha do tempo completa
    st.markdown("#### 📉 Tendência Correlacionada (Temperatura + Vibração)")
    fig_dual = go.Figure()
    fig_dual.add_trace(go.Scatter(
        x=df["timestamp"], y=df["temperatura"],
        name="Temperatura (°C)", yaxis="y1",
        line=dict(color="#3B82F6", width=1.5),
        hovertemplate="%{x|%d/%m %H:%M}<br>Temp: <b>%{y:.1f}°C</b><extra></extra>"
    ))
    fig_dual.add_trace(go.Scatter(
        x=df["timestamp"], y=df["vibracao"],
        name="Vibração (mm/s)", yaxis="y2",
        line=dict(color="#22C55E", width=1.5),
        hovertemplate="%{x|%d/%m %H:%M}<br>Vib: <b>%{y:.2f} mm/s</b><extra></extra>"
    ))
    fig_dual.update_layout(
        paper_bgcolor="#1E2233", plot_bgcolor="#1E2233",
        font=dict(color="#8B9AC0", size=11),
        xaxis=dict(gridcolor="#252A3D"),
        yaxis=dict(title="Temperatura (°C)", gridcolor="#252A3D", color="#3B82F6"),
        yaxis2=dict(title="Vibração (mm/s)", overlaying="y", side="right", color="#22C55E", gridcolor="#252A3D"),
        legend=dict(orientation="h", y=1.02, bgcolor="rgba(0,0,0,0)"),
        height=280, margin=dict(l=0, r=0, t=10, b=0),
        hovermode="x unified"
    )
    st.plotly_chart(fig_dual, use_container_width=True)

    st.caption(f"ℹ **Como integrar seus dados reais:** substitua a função `carregar_dados_historicos()` "
               f"por `pd.read_csv('seu_arquivo.csv')` ou uma query SQL. "
               f"Mantenha as colunas `timestamp`, `temperatura` e `vibracao`.")

# ── TAB 2: ALARMES ──
with tab2:
    st.markdown("### 🚨 Log de Alarmes e Eventos")

    ALARMES = {
        "MT-002": [
            ("warn", "06:14", "Vibração elevada — 3.9 mm/s (limite: 4.5 mm/s). Monitorar evolução."),
            ("warn", "03:52", "Temperatura em ascensão — tendência +0.4°C/h nas últimas 6h."),
            ("info", "Ontem", "Manutenção preventiva realizada. Lubrificação dos rolamentos OK."),
        ],
        "MT-004": [
            ("crit", "08:01", "CRÍTICO — Temperatura acima do limite — 71°C (limite: 60°C). Intervenção imediata!"),
            ("crit", "07:44", "CRÍTICO — Vibração excessiva — 5.8 mm/s (limite: 4.5 mm/s). Risco de falha mecânica."),
            ("warn", "05:30", "Corrente elevada — 52.0 A. Verificar carga e rolamentos."),
            ("warn", "02:11", "Tendência de aquecimento detectada via análise preditiva."),
        ],
    }

    alarmes_tag = ALARMES.get(tag, [])
    if not alarmes_tag:
        st.success("✅ Nenhum alarme ativo para este ativo nas últimas 24h.")
    else:
        for nivel, hora, msg in alarmes_tag:
            css = f"alarme-{nivel}"
            icon = "🔴" if nivel == "crit" else "🟡" if nivel == "warn" else "🟢"
            st.markdown(
                f'<div class="{css}"><strong>{icon} {hora}</strong> — {msg}</div>',
                unsafe_allow_html=True
            )

    st.divider()
    st.markdown("#### 📋 Estatísticas do Período (Últimas 48h)")
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    col_s1.metric("Temp. Máxima", f"{df['temperatura'].max():.1f} °C")
    col_s2.metric("Temp. Média", f"{df['temperatura'].mean():.1f} °C")
    col_s3.metric("Vib. Máxima", f"{df['vibracao'].max():.2f} mm/s")
    col_s4.metric("Vib. Média", f"{df['vibracao'].mean():.2f} mm/s")

    # Histograma de distribuição de temperatura
    st.markdown("#### 📊 Distribuição de Temperatura")
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=df["temperatura"], nbinsx=20,
        marker_color="#3B82F6", opacity=0.8,
        name="Temperatura",
        hovertemplate="Faixa: %{x:.1f}°C<br>Ocorrências: %{y}<extra></extra>"
    ))
    fig_hist.add_vline(x=LIMITES["temp"], line_dash="dash", line_color="#EF4444",
                       annotation_text="Limite Crítico", annotation_font_color="#EF4444")
    fig_hist.update_layout(
        paper_bgcolor="#1E2233", plot_bgcolor="#1E2233",
        font=dict(color="#8B9AC0", size=11),
        xaxis=dict(title="Temperatura (°C)", gridcolor="#252A3D"),
        yaxis=dict(title="Frequência", gridcolor="#252A3D"),
        showlegend=False, height=220, margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# ── TAB 3: IDENTIFICAÇÃO VISUAL ──
with tab3:
    st.markdown("### 🔍 Placa de Identificação e Cadastro")

    col_id1, col_id2 = st.columns(2)

    with col_id1:
        st.markdown("**Placa de Identificação (Simulada)**")
        st.markdown(f"""
        <div class="id-plate">
            <b>Fabricante:</b> {info['modelo'].split()[0]}<br>
            <b>Modelo:</b> {info['modelo']}<br>
            <b>Potência:</b> {info['potencia']}<br>
            <b>Tensão:</b> {info['tensao']}<br>
            <b>Classe IP:</b> {info['ip']}<br>
            <b>N° Série:</b> {info['serie']}<br>
            <b>TAG Ativo:</b> {tag}
        </div>
        """, unsafe_allow_html=True)

        st.caption("💡 Para integrar imagens reais, use: `st.image('caminho/placa.jpg', caption='Placa de Identificação')`")

        # Placeholder visual de imagem da placa
        st.markdown("**Imagem da Placa (placeholder — substitua pelo arquivo real):**")
        fig_placeholder = go.Figure()
        fig_placeholder.add_annotation(
            text=f"📷 Imagem da Placa<br>{tag}<br><br>Adicionar foto via visão computacional<br>ou upload manual",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=14, color="#4B5780"),
            align="center"
        )
        fig_placeholder.add_shape(
            type="rect", x0=0, y0=0, x1=1, y1=1,
            xref="paper", yref="paper",
            line=dict(color="#252A3D", dash="dash"), fillcolor="#1E2233"
        )
        fig_placeholder.update_layout(
            paper_bgcolor="#161923", height=200,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(visible=False), yaxis=dict(visible=False)
        )
        st.plotly_chart(fig_placeholder, use_container_width=True)

    with col_id2:
        st.markdown("**Dados do Cadastro do Ativo**")
        st.markdown(f"""
        <div class="id-plate">
            <b>TAG:</b> {tag}<br>
            <b>Nome:</b> {info['nome']}<br>
            <b>Localização:</b> {planta}<br>
            <b>Data de Instalação:</b> {info['instalacao']}<br>
            <b>RPM Nominal:</b> {info['rpm']} RPM<br>
            <b>Corrente Nominal:</b> {info['corrente']} A<br>
            <b>Próx. Manutenção:</b> Jul/2026<br>
            <b>Responsável:</b> Manutenção Elétrica
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.markdown("**Rastreabilidade do Ativo**")
        rastreabilidade = pd.DataFrame({
            "Evento": ["Instalação", "Manutenção Preventiva", "Troca de Rolamentos", "Calibração Sensores", "Inspeção Visual"],
            "Data": ["Jan/2023", "Jul/2023", "Jan/2024", "Mar/2024", "Jun/2025"],
            "Técnico": ["Equipe A", "Equipe B", "Equipe A", "Equipe C", "Equipe B"],
            "Status": ["✅ OK", "✅ OK", "✅ OK", "✅ OK", "✅ OK"]
        })
        st.dataframe(
            rastreabilidade, use_container_width=True, hide_index=True,
            column_config={
                "Evento": st.column_config.TextColumn("Evento"),
                "Data": st.column_config.TextColumn("Data"),
            }
        )

# ─────────────────────────────────────────────
# RODAPÉ
# ─────────────────────────────────────────────
st.divider()
st.caption(
    "⚠ **Aviso:** Todos os dados de telemetria são **simulados proceduralmente** para fins de demonstração. "
    "Substitua a função `carregar_dados_historicos()` pela integração com os dados da Sprint 1 (CSV ou SQL). "
    f" | Dashboard atualizado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}"
)
