import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Executive CRM", layout="wide")

# --- CORES IDENTIDADE ---
COLOR_LEAD, COLOR_KALIL, COLOR_OUTRO, TEXT_COLOR = "#8B4513", "#FFB347", "#C06C4D", "#FFFFFF"

# --- CSS RESPONSIVO E COMPACTO ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0F172A; }}
    .block-container {{ padding: 0.5rem 1rem !important; }}
    
    /* Força variáveis de texto do Streamlit e cor global */
    :root {{
        --text-color: #FFFFFF !important;
        --secondary-text-color: #94A3B8 !important;
    }}
    
    * {{ color: #FFFFFF !important; }}
    
    /* Força cor branca em títulos e textos fora dos gráficos */
    .main-title, .metric-value, .stMarkdown p, label {{
        color: #FFFFFF !important;
    }}

    header, footer, .stDeployButton {{ visibility: hidden; display: none; }}
    
    .main-title {{ font-size: 1.1rem !important; font-weight: bold; margin-bottom: 10px; }}
    
    /* Container da linha de canal */
    .channel-row {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 5px;
        padding: 4px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }}

    .channel-badge {{
        min-width: 60px;
        font-weight: 800;
        font-size: 0.75rem;
        padding: 2px 6px;
        border-radius: 4px;
        text-align: center;
    }}

    /* Card de métrica em linha única */
    .custom-metric {{
        background-color: #1E293B;
        border: 1px solid #334155;
        padding: 4px 10px;
        border-radius: 4px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-grow: 1;
        min-width: 150px;
    }}
    
    .metric-label {{ font-size: 0.7rem; color: #94A3B8 !important; text-transform: uppercase; margin-right: 8px; }}
    .metric-value {{ font-size: 0.85rem; font-weight: bold; }}
    .metric-delta {{ font-size: 0.75rem; font-weight: bold; margin-left: 5px; }}

    /* Força fundo escuro e letra branca nos filtros independente do tema do navegador */
    div[data-baseweb="select"] > div {{
        background-color: #1E293B !important;
        color: #FFFFFF !important;
    }}
    div[data-baseweb="popover"] * {{
        background-color: #1E293B !important;
        color: #FFFFFF !important;
    }}
    
    @media (max-width: 768px) {{
        .channel-row {{ flex-direction: column; align-items: flex-start; }}
        .custom-metric {{ width: 100%; }}
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
            if col in df.columns: df[col] = df[col].apply(clean_currency).fillna(0)
        df['Canal_Agrupado'] = df['Canal'].apply(lambda x: x if x in ['Lead', 'Kalil'] else 'Outro')
        df['Total Pago'] = df['Entrada'] + df['Segundo_Pagto']
        df['Saldo Total'] = df['Valor'] - df['Total Pago']
        df['Pago Vista'] = df.apply(lambda x: x['Valor'] if x['Entrada'] == x['Valor'] and x['Valor'] > 0 else 0, axis=1)
        df['Pago Parcelado'] = df.apply(lambda x: x['Total Pago'] if x['Entrada'] < x['Valor'] else 0, axis=1)
        df['Saldo Parcelado'] = df.apply(lambda x: x['Saldo Total'] if x['Entrada'] < x['Valor'] else 0, axis=1)
        return df
    except: return pd.DataFrame()

df_base = load_data()

if not df_base.empty:
    col_t, col_f1, col_f2 = st.columns([2, 1, 1])
    col_t.markdown('<p class="main-title">📊 CRM Executive</p>', unsafe_allow_html=True)
    
    # Filtro de Mês
    meses = ["Total"] + sorted(df_base['Mês'].dropna().unique().tolist())
    mes_filtro = col_f1.selectbox("", meses, label_visibility="collapsed")

    # Filtro de Outro/Indicador
    outros_unicos = sorted([c for c in df_base['Canal'].dropna().unique() if c not in ['Lead', 'Kalil']])
    opcoes_outro = ["Todos os Outros"] + outros_unicos
    outro_filtro = col_f2.selectbox("", opcoes_outro, label_visibility="collapsed")

    # Aplicação dos Filtros
    df = df_base if mes_filtro == "Total" else df_base[df_base['Mês'] == mes_filtro]
    
    # Lógica Dinâmica do Canal "Outro"
    nome_outro_agrupado = "Outro"
    PALETA_MAP_DYNAMIC = {"Lead": COLOR_LEAD, "Kalil": COLOR_KALIL, "Outro": COLOR_OUTRO}

    if outro_filtro != "Todos os Outros":
        df = df[df['Canal'].isin(['Lead', 'Kalil', outro_filtro])].copy()
        df.loc[df['Canal'] == outro_filtro, 'Canal_Agrupado'] = outro_filtro
        nome_outro_agrupado = outro_filtro
        PALETA_MAP_DYNAMIC = {"Lead": COLOR_LEAD, "Kalil": COLOR_KALIL, outro_filtro: COLOR_OUTRO}

    df_vendas = df[df['Total Pago'] > 0].copy()

    def custom_metric(label, value, delta=None, delta_color="#4ADE80"):
        delta_html = f"<span class='metric-delta' style='color:{delta_color} !important;'>({delta})</span>" if delta else ""
        return f"""
            <div class="custom-metric">
                <span class="metric-label">{label}</span>
                <span class="metric-value">€ {value:,.0f} {delta_html}</span>
            </div>
        """

    def render_channel_row(name, color):
        subset = df[df['Canal_Agrupado'] == name]
        if subset.empty and name == "Outro": return
        fat = subset['Valor'].sum()
        v, p, s = subset['Pago Vista'].sum(), subset['Pago Parcelado'].sum(), subset['Saldo Parcelado'].sum()
        def pct(val): return f"{((val/fat)*100):.0f}%" if fat > 0 else "0%"
        st.markdown(f"""
            <div class="channel-row">
                <div class="channel-badge" style="background-color: {color};">{name.upper()}</div>
                {custom_metric("Total", fat)}
                {custom_metric("À Vista", v, pct(v))}
                {custom_metric("Parcelado", p, pct(p))}
                {custom_metric("Saldo", s, pct(s), "#F87171")}
            </div>
        """, unsafe_allow_html=True)

    render_channel_row('Lead', COLOR_LEAD)
    render_channel_row('Kalil', COLOR_KALIL)
    render_channel_row(nome_outro_agrupado, COLOR_OUTRO)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- GRÁFICOS ---
    def estilo(fig):
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=TEXT_COLOR, size=11),
            title_font_color=TEXT_COLOR,
            margin=dict(l=5, r=5, t=35, b=5), height=210,
            hovermode=False, 
            legend=dict(
                orientation="h", yanchor="bottom", y=1.1, xanchor="right", x=1,
                font=dict(color=TEXT_COLOR)
            )
        )
        return fig

    conf = {'staticPlot': True}
    c1, c2, c3 = st.columns(3)

    with c1:
        fd = []
        for c in ["Lead", "Kalil", name_outro_agrupado]:
            sub = df[df['Canal_Agrupado'] == c]
            if not sub.empty:
                fd.append({'Etapa': 'Contatos', 'Canal': c, 'Qtd': len(sub)})
                fd.append({'Etapa': 'Clientes', 'Canal': c, 'Qtd': len(sub[sub['Total Pago'] > 0])})
        fig1 = px.funnel(pd.DataFrame(fd), x='Qtd', y='Etapa', color='Canal', title="Funil de Vendas", color_discrete_map=PALETA_MAP_DYNAMIC)
        fig1.update_traces(textfont=dict(color="white"))
        st.plotly_chart(estilo(fig1), use_container_width=True, config=conf)

    with c2:
        fig2 = px.bar(df_vendas.groupby("Categoria")["Valor"].sum().reset_index(), x="Valor", y="Categoria", orientation='h', title="Mix de Vendas (€)", color_discrete_sequence=[COLOR_LEAD])
        st.plotly_chart(estilo(fig2), use_container_width=True, config=conf)

    with c3:
        fig3 = px.bar(df_vendas.groupby(["Idade", "Canal_Agrupado"]).size().reset_index(name='Qtd'), x="Idade", y="Qtd", color="Canal_Agrupado", barmode='group', title="Vendas por Idade", color_discrete_map=PALETA_MAP_DYNAMIC)
        st.plotly_chart(estilo(fig3), use_container_width=True, config=conf)

    c4, c5, c6 = st.columns(3)
    with c4:
        fig4 = px.bar(df_vendas.groupby(["País", "Canal_Agrupado"]).size().reset_index(name='Qtd'), x="País", y="Qtd", color="Canal_Agrupado", barmode='group', title="Clientes por País", color_discrete_map=PALETA_MAP_DYNAMIC)
        st.plotly_chart(estilo(fig4), use_container_width=True, config=conf)

    with c5:
        fig5 = px.bar(df_vendas.groupby(["Idade", "Canal_Agrupado"])["Valor"].sum().reset_index(), x="Idade", y="Valor", color="Canal_Agrupado", barmode='group', title="Faturamento por Idade (€)", color_discrete_map=PALETA_MAP_DYNAMIC)
        st.plotly_chart(estilo(fig5), use_container_width=True, config=conf)

    with c6:
        # Prepara dados do Saldo Devedor: Resumo de Nome e Top 10
        df_saldo = df_vendas[df_vendas['Saldo Total'] > 0].copy()
        if not df_saldo.empty:
            def short_name(name):
                parts = str(name).split()
                return f"{parts[0]} {parts[-1]}" if len(parts) > 1 else parts[0]
            df_saldo['Cliente'] = df_saldo['Cliente'].apply(short_name)
            df_saldo = df_saldo.sort_values("Saldo Total", ascending=False).head(10)
            
            fig6 = px.bar(df_saldo, x="Cliente", y="Saldo Total", color="Canal_Agrupado", title="Top 10 Saldo Devedor (€)", color_discrete_map=PALETA_MAP_DYNAMIC)
            st.plotly_chart(estilo(fig6), use_container_width=True, config=conf)

st.write(""); st.write("")