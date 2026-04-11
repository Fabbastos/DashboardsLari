import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Executive CRM", layout="wide", page_icon="📊")

# --- CORES IDENTIDADE ---
COLOR_LEAD, COLOR_KALIL, TEXT_COLOR = "#8B4513", "#FFB347", "#FFFFFF"
PALETA_MAP = {"Lead": COLOR_LEAD, "Kalil": COLOR_KALIL}

# --- CSS RESPONSIVO ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0F172A; }}
    .block-container {{ padding: 1rem 1rem 5rem 1rem !important; }}
    
    /* Força cor branca universal para elementos HTML padrão */
    h1, h2, h3, p, span, label {{ color: {TEXT_COLOR} !important; }}
    
    /* FIX FILTRO SELECTBOX */
    div[data-baseweb="select"] > div {{
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
    }}
    
    header {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    
    .main-title {{ font-size: 1.3rem !important; font-weight: bold; margin-bottom: 15px; text-align: center; }}
    .channel-label {{ font-size: 1rem !important; font-weight: 800 !important; margin-top: 5px; border-bottom: 2px solid rgba(255,255,255,0.1); width: 100%; }}

    /* MÉTRICAS COMPACTAS */
    div[data-testid="stMetric"] {{ 
        background-color: #1E293B; 
        padding: 8px !important; /* Padding reduzido */
        border: 1px solid #334155; 
        border-radius: 8px;
        text-align: center;
    }}
    /* Reduzir tamanho das fontes dentro da métrica */
    div[data-testid="stMetricLabel"] > div {{ font-size: 0.75rem !important; }}
    div[data-testid="stMetricValue"] > div {{ font-size: 1rem !important; }}
    div[data-testid="stMetricDelta"] > div {{ font-size: 0.7rem !important; }}

    /* Ajuste para mobile: garantir que os gráficos não fiquem muito altos */
    @media (max-width: 768px) {{
        .stPlotlyChart {{ height: 200px !important; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. Funções de Dados
SHEET_ID = "1mVcogReqnHTyzAes_NJYu0MBHEDbqyj1_suJMGOnf0Q"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = [c.strip() for c in df.columns]
        
        def clean_currency(value):
            if pd.isna(value): return 0.0
            if isinstance(value, (int, float)): return float(value)
            clean_val = str(value).replace('€', '').replace('R$', '').strip()
            if '.' in clean_val and ',' in clean_val:
                clean_val = clean_val.replace('.', '').replace(',', '.')
            elif ',' in clean_val:
                clean_val = clean_val.replace(',', '.')
            return pd.to_numeric(clean_val, errors='coerce') or 0.0

        cols_financeiras = ['Valor', 'Entrada', 'Segundo_Pagto']
        for col in cols_financeiras:
            if col in df.columns:
                df[col] = df[col].apply(clean_currency)
            else:
                df[col] = 0.0

        df['Total Pago'] = df['Entrada'] + df['Segundo_Pagto']
        df['Saldo Total'] = df['Valor'] - df['Total Pago']
        
        df['Pago Vista'] = df.apply(lambda x: x['Valor'] if x['Entrada'] >= x['Valor'] and x['Valor'] > 0 else 0, axis=1)
        df['Pago Parcelado'] = df.apply(lambda x: x['Total Pago'] if x['Entrada'] < x['Valor'] else 0, axis=1)
        df['Saldo Parcelado'] = df.apply(lambda x: x['Saldo Total'] if x['Entrada'] < x['Valor'] else 0, axis=1)
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df_base = load_data()

# --- FUNÇÃO DE ESTILO CORRIGIDA PARA BRANCO ---
def aplicar_estilo(fig, is_bar=False, title_text=""):
    # Forçar cor branca explicitamente em todos os componentes do Plotly
    fig.update_layout(
        title=dict(text=title_text, font=dict(color="#FFFFFF", size=14)), # Título do Gráfico Branco
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#FFFFFF", size=10), # Fonte geral branca
        margin=dict(l=10, r=10, t=40, b=10), 
        height=220, # Ligeiramente menor
        hovermode="closest", 
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#FFFFFF"))
    )
    
    # Forçar eixos brancos
    axis_config = dict(
        titlefont=dict(color="#FFFFFF"), # Título do Eixo Branco
        tickfont=dict(color="#FFFFFF"),  # Números/Labels do Eixo Branco
        showgrid=False, 
        zeroline=False
    )
    
    fig.update_xaxes(**axis_config)
    fig.update_yaxes(**axis_config)

    if is_bar:
        fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
        
    return fig

if not df_base.empty:
    # --- CABEÇALHO ---
    st.markdown('<p class="main-title">📊 Executive CRM Dashboard</p>', unsafe_allow_html=True)
    
    meses = ["Total"] + sorted([m for m in df_base['Mês'].unique() if pd.notna(m)])
    # Selectbox centralizado e mais compacto no topo
    c_sel1, c_sel2, c_sel3 = st.columns([1, 2, 1])
    with c_sel2:
        mes_filtro = st.selectbox("Filtrar Período", meses, label_visibility="collapsed")

    df = df_base if mes_filtro == "Total" else df_base[df_base['Mês'] == mes_filtro]
    df_vendas = df[df['Total Pago'] > 0].copy()

    # --- MÉTRICAS ---
    def render_metrics(channel, color):
        subset = df[df['Canal'] == channel]
        fat = subset['Valor'].sum()
        st.markdown(f"<p class='channel-label' style='color:{color}'>{channel.upper()}</p>", unsafe_allow_html=True)
        
        # Colunas com larguras desiguais para compactar o meio
        m1, m2, m3, m4 = st.columns([1.2, 1, 1, 1.2])
        
        def fmt(val): return f"€ {val:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        def pct_label(p): return f"{(p / fat * 100):.1f}%" if fat > 0 else "0%"

        m1.metric("Faturamento", fmt(fat))
        
        v = subset['Pago Vista'].sum()
        m2.metric("À Vista", fmt(v), delta=pct_label(v))
        
        p = subset['Pago Parcelado'].sum()
        m3.metric("Pago (Parc.)", fmt(p), delta=pct_label(p))
        
        s = subset['Saldo Parcelado'].sum()
        m4.metric("A Receber", fmt(s), delta=pct_label(s), delta_color="inverse")

    render_metrics('Lead', COLOR_LEAD)
    render_metrics('Kalil', COLOR_KALIL)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # --- GRÁFICOS ---
    c1, c2, c3 = st.columns(3)

    with c1:
        fd = []
        for c in ["Lead", "Kalil"]:
            sub = df[df['Canal'] == c]
            fd.append({'Etapa': '1. Contatos', 'Canal': c, 'Qtd': len(sub)})
            fd.append({'Etapa': '2. Clientes', 'Canal': c, 'Qtd': len(sub[sub['Total Pago'] > 0])})
        fig1 = px.funnel(pd.DataFrame(fd), x='Qtd', y='Etapa', color='Canal', color_discrete_map=PALETA_MAP)
        # Título movido para dentro da função de estilo
        st.plotly_chart(aplicar_estilo(fig1, title_text="Conversão de Funil"), use_container_width=True, config={'displayModeBar': False})

    with c2:
        if not df_vendas.empty:
            mix = df_vendas.groupby("Categoria")["Valor"].sum().reset_index()
            fig2 = px.bar(mix, x="Valor", y="Categoria", orientation='h', color_discrete_sequence=[COLOR_KALIL])
            st.plotly_chart(aplicar_estilo(fig2, is_bar=True, title_text="Mix de Produtos (€)"), use_container_width=True, config={'displayModeBar': False})
        else: st.info("Sem vendas")

    with c3:
        if not df_vendas.empty:
            idade_df = df_vendas.groupby(["Idade", "Canal"]).size().reset_index(name='Qtd')
            fig3 = px.bar(idade_df, x="Idade", y="Qtd", color="Canal", barmode='group', color_discrete_map=PALETA_MAP)
            st.plotly_chart(aplicar_estilo(fig3, is_bar=True, title_text="Perfil por Idade"), use_container_width=True, config={'displayModeBar': False})

    c4, c5, c6 = st.columns(3)
    with c4:
        if not df_vendas.empty:
            pais_df = df_vendas.groupby(["País", "Canal"]).size().reset_index(name='Qtd')
            fig4 = px.bar(pais_df, x="País", y="Qtd", color="Canal", color_discrete_map=PALETA_MAP)
            st.plotly_chart(aplicar_estilo(fig4, is_bar=True, title_text="Distribuição Geográfica"), use_container_width=True, config={'displayModeBar': False})

    with c5:
        if not df_vendas.empty:
            fat_idade = df_vendas.groupby(["Idade", "Canal"])["Valor"].sum().reset_index()
            fig5 = px.bar(fat_idade, x="Idade", y="Valor", color="Canal", barmode='group', color_discrete_map=PALETA_MAP)
            st.plotly_chart(aplicar_estilo(fig5, is_bar=True, title_text="Faturamento por Idade"), use_container_width=True, config={'displayModeBar': False})

    with c6:
        saldo_df = df_vendas[df_vendas['Saldo Total'] > 0].sort_values('Saldo Total', ascending=False).head(10)
        if not saldo_df.empty:
            fig6 = px.bar(saldo_df, x="Cliente", y="Saldo Total", color="Canal", color_discrete_map=PALETA_MAP)
            st.plotly_chart(aplicar_estilo(fig6, is_bar=True, title_text="Top 10 Saldos"), use_container_width=True, config={'displayModeBar': False})
        else: st.info("Sem saldos")

else:
    st.error("Base de dados vazia ou inacessível.")