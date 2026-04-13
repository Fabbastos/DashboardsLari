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
    
    :root {{
        --text-color: #FFFFFF !important;
        --secondary-text-color: #94A3B8 !important;
    }}
    
    * {{ color: #FFFFFF !important; }}
    
    .main-title, .metric-value, .stMarkdown p, label {{
        color: #FFFFFF !important;
    }}

    header, footer, .stDeployButton {{ visibility: hidden; display: none; }}
    
    .main-title {{ font-size: 1.1rem !important; font-weight: bold; margin-bottom: 10px; }}
    
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
    
    meses = ["Total"] + sorted(df_base['Mês'].dropna().unique().tolist())
    mes_filtro = col_f1.selectbox("", meses, label_visibility="collapsed")

    outros_unicos = sorted([c for c in df_base['Canal'].dropna().unique() if c not in ['Lead', 'Kalil']])
    opcoes_outro = ["Todos os Outros"] + outros_unicos
    outro_filtro = col_f2.selectbox("", opcoes_outro, label_visibility="collapsed")

    df = df_base if mes_filtro == "Total" else df_base[df_base['Mês'] == mes_filtro]
    
    nome_outro_agrupado = "Outro"
    PALETA_MAP_DYNAMIC = {"Lead": COLOR_LEAD, "Kalil": COLOR_KALIL, "Outro": COLOR_OUTRO}

    if outro_filtro != "Todos os Outros":
        df = df[df['Canal'].isin(['Lead', 'Kalil', outro_filtro])].copy()
        df.loc[df['Canal'] == outro_filtro, 'Canal_Agrupado'] = outro_filtro
        nome_outro_agrupado = outro_filtro
        PALETA_MAP_DYNAMIC = {"Lead": COLOR_LEAD, "Kalil": COLOR_KALIL, outro_filtro: COLOR_OUTRO}

    df_vendas = df[df['Total Pago'] > 0].copy()

    # Lógica de Faixa Etária
    def agrupar_idade(idade):
        try:
            idade = int(float(idade))
            if idade <= 25: return "20-25"
            if idade <= 30: return "26-30"
            if idade <= 35: return "31-35"
            if idade <= 40: return "36-40"
            return "40+"
        except: return "N/D"

    df_vendas['Faixa Etária'] = df_vendas['Idade'].apply(agrupar_idade)
    ordem_faixas = ["20-25", "26-30", "31-35", "36-40", "40+"]
    ordem_canais = ["Lead", "Kalil", nome_outro_agrupado]

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

    # --- GRÁFICOS (VISUAL UPGRADE) ---
    def estilo(fig, show_y=True, show_x=True, integer_x=False, integer_y=False):
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=TEXT_COLOR, size=11),
            title=dict(x=0, font=dict(color=TEXT_COLOR, size=13)),
            margin=dict(l=10, r=10, t=40, b=10), height=230,
            hovermode=False, 
            legend=dict(
                orientation="v", yanchor="top", y=1, xanchor="left", x=1.02,
                font=dict(color=TEXT_COLOR, size=10), title=None
            ),
            xaxis=dict(showgrid=False, visible=show_x, title=None),
            yaxis=dict(showgrid=False, visible=show_y, title=None)
        )
        if integer_x: fig.update_xaxes(dtick=1)
        if integer_y: fig.update_yaxes(dtick=1)
        return fig

    conf = {'staticPlot': True}
    c1, c2, c3 = st.columns(3)

    with c1:
        fd = []
        for c in ordem_canais:
            sub = df[df['Canal_Agrupado'] == c]
            if not sub.empty:
                fd.append({'Etapa': 'Contatos', 'Canal': c, 'Qtd': len(sub)})
                fd.append({'Etapa': 'Clientes', 'Canal': c, 'Qtd': len(sub[sub['Total Pago'] > 0])})
        fig1 = px.funnel(pd.DataFrame(fd), x='Qtd', y='Etapa', color='Canal', title="Funil de Vendas", 
                         color_discrete_map=PALETA_MAP_DYNAMIC, category_orders={"Canal": ordem_canais})
        fig1.update_traces(textfont=dict(color="white"))
        st.plotly_chart(estilo(fig1, show_y=True, show_x=False), use_container_width=True, config=conf)

    with c2:
        fig2 = px.bar(df_vendas.groupby("Categoria")["Valor"].sum().reset_index().sort_values("Valor"), 
                      x="Valor", y="Categoria", orientation='h', title="Mix de Vendas (€)", 
                      color_discrete_sequence=[COLOR_LEAD], text_auto='.2s')
        fig2.update_traces(textposition='outside', cliponaxis=False)
        st.plotly_chart(estilo(fig2, show_x=False), use_container_width=True, config=conf)

    with c3:
        df_idade_qtd = df_vendas.groupby(["Faixa Etária", "Canal_Agrupado"]).size().reset_index(name='Qtd')
        fig3 = px.bar(df_idade_qtd, x="Faixa Etária", y="Qtd", color="Canal_Agrupado", barmode='group', 
                      title="Vendas por Idade", color_discrete_map=PALETA_MAP_DYNAMIC,
                      category_orders={"Faixa Etária": ordem_faixas, "Canal_Agrupado": ordem_canais})
        st.plotly_chart(estilo(fig3, integer_y=True), use_container_width=True, config=conf)

    c4, c5, c6 = st.columns(3)
    with c4:
        # Gráfico 4: Clientes por País (Barras Horizontais Empilhadas)
        df_pais = df_vendas.groupby(["País", "Canal_Agrupado"]).size().reset_index(name='Qtd')
        pais_order = df_vendas.groupby("País").size().sort_values().index.tolist()
        fig4 = px.bar(df_pais, y="País", x="Qtd", color="Canal_Agrupado", barmode='stack', orientation='h',
                      title="Clientes por País", color_discrete_map=PALETA_MAP_DYNAMIC,
                      category_orders={"País": pais_order, "Canal_Agrupado": ordem_canais}, text_auto=True)
        st.plotly_chart(estilo(fig4, show_x=False, integer_x=True), use_container_width=True, config=conf)

    with c5:
        df_idade_valor = df_vendas.groupby(["Faixa Etária", "Canal_Agrupado"])["Valor"].sum().reset_index()
        fig5 = px.bar(df_idade_valor, x="Faixa Etária", y="Valor", color="Canal_Agrupado", barmode='group', 
                      title="Faturamento por Idade (€)", color_discrete_map=PALETA_MAP_DYNAMIC,
                      category_orders={"Faixa Etária": ordem_faixas, "Canal_Agrupado": ordem_canais})
        st.plotly_chart(estilo(fig5), use_container_width=True, config=conf)

    with c6:
        # Gráfico 6: Top 5 Devedores (Barras Horizontais com Destaque)
        df_saldo = df_vendas[df_vendas['Saldo Total'] > 0].copy()
        if not df_saldo.empty:
            def treat_name(name):
                clean = str(name).replace("[", "").replace("]", "").replace("'", "").replace(",", "")
                return (clean[:15] + '..') if len(clean) > 16 else clean

            df_saldo['Cliente'] = df_saldo['Cliente'].apply(treat_name)
            df_saldo = df_saldo.sort_values("Saldo Total", ascending=False).head(5)
            
            # Reverter ordem para que o maior fique no topo no gráfico horizontal
            df_saldo = df_saldo.iloc[::-1]
            
            fig6 = px.bar(df_saldo, y="Cliente", x="Saldo Total", color="Canal_Agrupado", 
                          orientation='h', title="Top 5 Devedores (€)", 
                          color_discrete_map=PALETA_MAP_DYNAMIC,
                          category_orders={"Canal_Agrupado": ordem_canais}, text_auto=',.0f')
            
            # Ajuste de destaque: Reduzir opacidade de quem não é o Top 1
            opacities = [0.4] * (len(df_saldo)-1) + [1.0]
            fig6.update_traces(marker_opacity=opacities, textposition='outside', cliponaxis=False)
            
            st.plotly_chart(estilo(fig6, show_x=False), use_container_width=True, config=conf)

st.write(""); st.write("")