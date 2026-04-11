import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Executive CRM", layout="wide")

# --- CORES IDENTIDADE ---
COLOR_LEAD, COLOR_KALIL, TEXT_COLOR = "#8B4513", "#FFB347", "#FFFFFF"
PALETA_MAP = {"Lead": COLOR_LEAD, "Kalil": COLOR_KALIL}

# --- CSS RESPONSIVO + FILTRO ESCURO MOBILE ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0F172A; }}
    .block-container {{ padding: 0.2rem 1rem 5rem 1rem !important; }}
    * {{ color: #FFFFFF !important; }}
    header {{ visibility: hidden; height: 0px; }}
    footer {{ visibility: hidden; }}
    .stDeployButton {{ display:none; }}
    
    .main-title {{ font-size: 1.2rem !important; font-weight: bold; margin: 10px 0px !important; }}
    .channel-label {{ font-size: 1.1rem !important; font-weight: 800 !important; margin-bottom: 5px !important; border-bottom: 1px solid rgba(255,255,255,0.1); display: inline-block; width: 100%; }}

    /* Estilização dos Cards */
    div[data-testid="stMetric"] {{ 
        background-color: #1E293B; 
        padding: 8px 12px !important; 
        border: 1px solid #334155; 
        min-height: 65px !important;
        height: auto !important;
    }}
    
    div[data-testid="stMetric"] > div {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        align-items: baseline !important;
        gap: 5px 10px !important;
    }}

    div[data-testid="stMetricLabel"] {{ 
        font-size: 0.75rem !important; 
        color: #CBD5E1 !important; 
        margin-bottom: 2px !important;
        width: 100%;
    }}
    
    div[data-testid="stMetricValue"] {{ 
        font-size: 1.1rem !important; 
        font-weight: bold; 
        line-height: 1.1;
        white-space: nowrap;
    }}
    
    div[data-testid="stMetricDelta"] {{ 
        font-size: 0.85rem !important; 
        font-weight: 500 !important;
        display: flex;
        align-items: center;
        white-space: nowrap;
    }}

    /* FILTRO ESCURO MOBILE E AJUSTES */
    @media (max-width: 768px) {{
        .stApp {{
            background-color: #070B14 !important; /* Fundo ainda mais escuro no mobile */
        }}
        [data-testid="stMetric"] {{
            background-color: #131C2E !important; /* Cards mais profundos */
            border-color: #1E293B !important;
        }}
        [data-testid="column"] {{ 
            width: 100% !important; 
            flex: 1 1 100% !important; 
            margin-bottom: 8px; 
        }}
        div[data-testid="stMetricValue"] {{ font-size: 1.0rem !important; }}
        
        /* Aplica uma leve dessaturação para reduzir cansaço visual no brilho do celular */
        img, .stPlotlyChart {{
            filter: brightness(0.9) contrast(1.1);
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. Conexão com a Planilha
SHEET_ID = "1mVcogReqnHTyzAes_NJYu0MBHEDbqyj1_suJMGOnf0Q"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = [c.strip() for c in df.columns]

        def clean_currency(value):
            if isinstance(value, str):
                clean_val = value.replace('€', '').replace('.', '').replace(',', '.').strip()
                return pd.to_numeric(clean_val, errors='coerce')
            return value

        for col in ['Valor', 'Entrada', 'Segundo_Pagto']:
            if col in df.columns:
                df[col] = df[col].apply(clean_currency).fillna(0)

        df['Total Pago'] = df['Entrada'] + df['Segundo_Pagto']
        df['Saldo Total'] = df['Valor'] - df['Total Pago']
        df['Pago Vista'] = df.apply(lambda x: x['Valor'] if x['Entrada'] == x['Valor'] and x['Valor'] > 0 else 0, axis=1)
        df['Pago Parcelado'] = df.apply(lambda x: x['Total Pago'] if x['Entrada'] < x['Valor'] else 0, axis=1)
        df['Saldo Parcelado'] = df.apply(lambda x: x['Saldo Total'] if x['Entrada'] < x['Valor'] else 0, axis=1)
        return df
    except:
        return pd.DataFrame()

df_base = load_data()

if not df_base.empty:
    # --- CABEÇALHO ---
    head_col1, head_col2 = st.columns([4, 1])
    with head_col1:
        st.markdown('<p class="main-title">📊 Executive CRM Dashboard</p>', unsafe_allow_html=True)
    with head_col2:
        meses = ["Total"] + sorted(df_base['Mês'].dropna().unique().tolist())
        mes_filtro = st.selectbox("", meses, label_visibility="collapsed")

    df = df_base if mes_filtro == "Total" else df_base[df_base['Mês'] == mes_filtro]
    df_vendas = df[df['Total Pago'] > 0].copy()

    # --- MÉTRICAS ---
    def render_metrics(channel, color):
        subset = df[df['Canal'] == channel]
        fat = subset['Valor'].sum()
        st.markdown(f"<p class='channel-label' style='color:{color}'>{channel}</p>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        
        m1.metric("Faturamento", f"€ {fat:,.0f}".replace(',', '.'))
        
        def pct(parte):
            return (parte / fat * 100) if fat > 0 else 0

        v = subset['Pago Vista'].sum()
        m2.metric("Pago à Vista", f"€ {v:,.0f}".replace(',', '.'), delta=f"{pct(v):.0f}%")
        
        p = subset['Pago Parcelado'].sum()
        m3.metric("Pago Parcelado", f"€ {p:,.0f}".replace(',', '.'), delta=f"{pct(p):.0f}%")
        
        s = subset['Saldo Parcelado'].sum()
        m4.metric("Saldo Parcelado", f"€ {s:,.0f}".replace(',', '.'), delta=f"{pct(s):.0f}%", delta_color="inverse")

    render_metrics('Lead', COLOR_LEAD)
    render_metrics('Kalil', COLOR_KALIL)
    st.markdown("<hr>", unsafe_allow_html=True)

    # --- GRÁFICOS ---
    def estilo(fig):
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=TEXT_COLOR, size=11), margin=dict(l=5, r=5, t=35, b=5), height=210,
            hovermode=False, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        return fig

    conf = {'staticPlot': True}
    c1, c2, c3 = st.columns(3)

    with c1:
        fd = []
        for c in ["Lead", "Kalil"]:
            sub = df[df['Canal'] == c]
            fd.append({'Etapa': '1. Contatos', 'Canal': c, 'Qtd': len(sub)})
            fd.append({'Etapa': '2. Clientes', 'Canal': c, 'Qtd': len(sub[sub['Total Pago'] > 0])})
        fig1 = px.funnel(pd.DataFrame(fd), x='Qtd', y='Etapa', color='Canal', title="Funil de Vendas", color_discrete_map=PALETA_MAP)
        fig1.update_traces(textinfo="value+percent initial")
        st.plotly_chart(estilo(fig1), use_container_width=True, config=conf)

    with c2:
        fig2 = px.bar(df_vendas.groupby("Categoria")["Valor"].sum().reset_index(), x="Valor", y="Categoria", orientation='h', title="Mix de Vendas (€)", color_discrete_sequence=[COLOR_LEAD])
        st.plotly_chart(estilo(fig2), use_container_width=True, config=conf)

    with c3:
        fig3 = px.bar(df_vendas.groupby(["Idade", "Canal"]).size().reset_index(name='Qtd'), x="Idade", y="Qtd", color="Canal", barmode='group', title="Vendas por Idade", color_discrete_map=PALETA_MAP)
        fig3.update_xaxes(categoryorder='category ascending')
        st.plotly_chart(estilo(fig3), use_container_width=True, config=conf)

    c4, c5, c6 = st.columns(3)
    with c4:
        fig4 = px.bar(df_vendas.groupby(["País", "Canal"]).size().reset_index(name='Qtd'), x="País", y="Qtd", color="Canal", barmode='group', title="Clientes por País", color_discrete_map=PALETA_MAP)
        st.plotly_chart(estilo(fig4), use_container_width=True, config=conf)

    with c5:
        fig5 = px.bar(df_vendas.groupby(["Idade", "Canal"])["Valor"].sum().reset_index(), x="Idade", y="Valor", color="Canal", barmode='group', title="Faturamento por Idade (€)", color_discrete_map=PALETA_MAP)
        fig5.update_xaxes(categoryorder='category ascending')
        st.plotly_chart(estilo(fig5), use_container_width=True, config=conf)

    with c6:
        fig6 = px.bar(df_vendas[df_vendas['Saldo Total'] > 0], x="Cliente", y="Saldo Total", color="Canal", title="Saldo Devedor por Cliente (€)", color_discrete_map=PALETA_MAP)
        st.plotly_chart(estilo(fig6), use_container_width=True, config=conf)

st.write(""); st.write("")