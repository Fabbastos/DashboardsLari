import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Executive CRM", layout="wide")

# --- CORES IDENTIDADE ---
COLOR_LEAD, COLOR_KALIL, TEXT_COLOR = "#5BC0EB", "#A05195", "#FFFFFF"
PALETA_MAP = {"Lead": COLOR_LEAD, "Kalil": COLOR_KALIL}

# --- CSS RESPONSIVO E CORREÇÃO DE CORES ---
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

    div[data-testid="stMetric"] {{ background-color: #1E293B; padding: 2px 10px !important; border: 1px solid #334155; height: 55px !important; }}
    div[data-testid="stMetricLabel"] {{ font-size: 0.72rem !important; color: #CBD5E1 !important; margin-bottom: -15px; }}
    div[data-testid="stMetricValue"] {{ font-size: 1.1rem !important; font-weight: bold; }}

    div.stButton > button {{
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        color: white !important;
        width: 100%;
        font-weight: bold;
    }}

    @media (max-width: 768px) {{
        [data-testid="column"] {{ width: 100% !important; flex: 1 1 100% !important; margin-bottom: 12px; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. Conexão Direta com sua Planilha
# Link convertido para exportação automática de CSV
SHEET_ID = "1mVcogReqnHTyzAes_NJYu0MBHEDbqyj1_suJMGOnf0Q"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = [c.strip() for c in df.columns]

        # Função interna para limpar moedas e converter para número
        def clean_currency(value):
            if isinstance(value, str):
                # Remove símbolo de Euro, pontos de milhar e espaços
                clean_val = value.replace('€', '').replace('.', '').replace(',', '.').strip()
                return pd.to_numeric(clean_val, errors='coerce')
            return value

        # Colunas que precisam ser numéricas para cálculos
        cols_financeiras = ['Valor', 'Entrada', 'Segundo_Pagto']
        for col in cols_financeiras:
            if col in df.columns:
                df[col] = df[col].apply(clean_currency).fillna(0)

        # Agora os cálculos matemáticos funcionarão sem erro de "str"
        df['Total Pago'] = df['Entrada'] + df['Segundo_Pagto']
        df['Saldo Total'] = df['Valor'] - df['Total Pago']
        
        df['Pago Vista'] = df.apply(
            lambda x: x['Valor'] if x['Entrada'] == x['Valor'] and x['Valor'] > 0 else 0, axis=1
        )
        df['Pago Parcelado'] = df.apply(
            lambda x: x['Total Pago'] if x['Entrada'] < x['Valor'] else 0, axis=1
        )
        df['Saldo Parcelado'] = df.apply(
            lambda x: x['Saldo Total'] if x['Entrada'] < x['Valor'] else 0, axis=1
        )
        
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com a planilha: {e}")
        return pd.DataFrame()

df_base = load_data()

if not df_base.empty:
    # --- CABEÇALHO ---
    head_col1, head_col2, head_col3 = st.columns([2.5, 1.2, 1])
    with head_col1:
        st.markdown('<p class="main-title">📊 Executive CRM Dashboard</p>', unsafe_allow_html=True)
    with head_col2:
        st.link_button("🔗 ACESSAR PLANILHA", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
    with head_col3:
        # Pega meses únicos da sua planilha
        meses_disponiveis = ["Total"] + sorted(df_base['Mês'].dropna().unique().tolist())
        mes_filtro = st.selectbox("", meses_disponiveis, label_visibility="collapsed")

    # Filtros de Dados
    df = df_base if mes_filtro == "Total" else df_base[df_base['Mês'] == mes_filtro]
    df_vendas = df[df['Total Pago'] > 0].copy()

    # --- MÉTRICAS ---
    def render_metrics(channel, color):
        subset = df[df['Canal'] == channel]
        st.markdown(f"<p class='channel-label' style='color:{color}'>{channel}</p>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Faturamento", f"€ {subset['Valor'].sum():,.0f}".replace(',', '.'))
        m2.metric("Pago à Vista", f"€ {subset['Pago Vista'].sum():,.0f}".replace(',', '.'))
        m3.metric("Pago Parcelado", f"€ {subset['Pago Parcelado'].sum():,.0f}".replace(',', '.'))
        m4.metric("Saldo Parcelado", f"€ {subset['Saldo Parcelado'].sum():,.0f}".replace(',', '.'))

    render_metrics('Lead', COLOR_LEAD)
    render_metrics('Kalil', COLOR_KALIL)
    st.markdown("<hr>", unsafe_allow_html=True)

    # --- CONFIG GRÁFICOS ---
    def aplicar_estilo(fig):
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=TEXT_COLOR, size=11), margin=dict(l=10, r=10, t=35, b=5), height=200,
            hovermode=False, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        return fig

    config_est = {'staticPlot': True}
    c1, c2, c3 = st.columns(3)

    with c1:
        funnel_data = []
        for c in ["Lead", "Kalil"]:
            sub = df[df['Canal'] == c]
            funnel_data.append({'Etapa': '1. Contatos', 'Canal': c, 'Qtd': len(sub)})
            funnel_data.append({'Etapa': '2. Clientes', 'Canal': c, 'Qtd': len(sub[sub['Total Pago'] > 0])})
        fig1 = px.funnel(pd.DataFrame(funnel_data), x='Qtd', y='Etapa', color='Canal', title="Funil de Vendas", color_discrete_map=PALETA_MAP)
        st.plotly_chart(aplicar_estilo(fig1), use_container_width=True, config=config_est)

    with c2:
        fig2 = px.bar(df_vendas.groupby("Categoria")["Valor"].sum().reset_index(), x="Valor", y="Categoria", orientation='h', title="Mix de Vendas (€)", color_discrete_sequence=[COLOR_LEAD])
        st.plotly_chart(aplicar_estilo(fig2), use_container_width=True, config=config_est)

    with c3:
        fig3 = px.bar(df_vendas.groupby(["Idade", "Canal"]).size().reset_index(name='Qtd'), x="Idade", y="Qtd", color="Canal", barmode='group', title="Vendas por Idade", color_discrete_map=PALETA_MAP)
        fig3.update_xaxes(categoryorder='category ascending')
        st.plotly_chart(aplicar_estilo(fig3), use_container_width=True, config=config_est)

    c4, c5, c6 = st.columns(3)
    with c4:
        fig4 = px.bar(df_vendas.groupby(["País", "Canal"]).size().reset_index(name='Qtd'), x="País", y="Qtd", color="Canal", barmode='group', title="Clientes por País", color_discrete_map=PALETA_MAP)
        st.plotly_chart(aplicar_estilo(fig4), use_container_width=True, config=config_est)

    with c5:
        fig5 = px.bar(df_vendas.groupby(["Idade", "Canal"])["Valor"].sum().reset_index(), x="Idade", y="Valor", color="Canal", barmode='group', title="Faturamento por Idade (€)", color_discrete_map=PALETA_MAP)
        fig5.update_xaxes(categoryorder='category ascending')
        st.plotly_chart(aplicar_estilo(fig5), use_container_width=True, config=config_est)

    with c6:
        # Mostra apenas clientes com dívida pendente
        fig6 = px.bar(df_vendas[df_vendas['Saldo Total'] > 0], x="Cliente", y="Saldo Total", color="Canal", title="Saldo Devedor (€)", color_discrete_map=PALETA_MAP)
        st.plotly_chart(aplicar_estilo(fig6), use_container_width=True, config=config_est)

st.write(""); st.write("")