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
    
    .main-title {{ font-size: 1.3rem !important; font-weight: bold; margin-bottom: 10px; }}
    
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

    .global-legend {{
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-bottom: 10px;
        font-size: 0.8rem;
    }}

    .legend-item {{
        display: flex;
        align-items: center;
        gap: 6px;
    }}

    .legend-color {{
        width: 12px;
        height: 12px;
        border-radius: 2px;
    }}

    div[data-baseweb="select"] > div {{
        background-color: #1E293B !important;
        color: #FFFFFF !important;
    }}
    
    @media (max-width: 768px) {{
        .channel-row {{ flex-direction: column; align-items: flex-start; }}
        .custom-metric {{ width: 100%; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. Conexão e Carga de Dados
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

def format_number(x):
    if x >= 1000: return f"{x/1000:.1f}k"
    return f"{int(x)}"

if not df_base.empty:
    # --- FILTROS ---
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

    # --- FUNÇÕES AUXILIARES DE INTERFACE ---
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

    # --- RENDERIZAR CARTÕES ---
    render_channel_row('Lead', COLOR_LEAD)
    render_channel_row('Kalil', COLOR_KALIL)
    render_channel_row(nome_outro_agrupado, COLOR_OUTRO)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- LEGENDA GLOBAL ---
    st.markdown(f"""
        <div class="global-legend">
            <div class="legend-item"><div class="legend-color" style="background:{COLOR_LEAD}"></div>Lead</div>
            <div class="legend-item"><div class="legend-color" style="background:{COLOR_KALIL}"></div>Kalil</div>
            <div class="legend-item"><div class="legend-color" style="background:{COLOR_OUTRO}"></div>Outro</div>
        </div>
    """, unsafe_allow_html=True)

    def estilo(fig, show_y=True, show_x=True, integer_x=False, integer_y=False):
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=TEXT_COLOR, size=12),
            title=dict(x=0, font=dict(color=TEXT_COLOR, size=18)),
            margin=dict(l=60, r=40, t=40, b=10), height=230,
            hovermode=False, showlegend=False,
            xaxis=dict(showgrid=False, visible=show_x, title=None, automargin=True),
            yaxis=dict(showgrid=False, visible=show_y, title=None, automargin=True)
        )
        if integer_x: fig.update_xaxes(dtick=1)
        if integer_y: fig.update_yaxes(dtick=1)
        return fig

    conf = {'staticPlot': True}
    c1, c2, c3 = st.columns(3)

    with c1:
        fd = []
        for c in ["Lead", "Kalil", nome_outro_agrupado]:
            sub = df[df['Canal_Agrupado'] == c]
            if not sub.empty:
                fd.append({'Etapa': 'Contatos', 'Canal': c, 'Qtd': len(sub)})
                fd.append({'Etapa': 'Clientes', 'Canal': c, 'Qtd': len(sub[sub['Total Pago'] > 0])})
        fig1 = px.funnel(pd.DataFrame(fd), x='Qtd', y='Etapa', color='Canal',
                         title="Funil de Vendas", color_discrete_map=PALETA_MAP_DYNAMIC)
        st.plotly_chart(estilo(fig1, show_y=True, show_x=False), use_container_width=True, config=conf)

    with c2:
        # 1. Agrupamos por Categoria E Canal para ter a divisão de cores
        df_mix = df_vendas.groupby(["Categoria", "Canal_Agrupado"])["Valor"].sum().reset_index()
        
        # 2. Ordenação: Menor na esquerda, Maior na direita (dentro da barra)
        df_mix = df_mix.sort_values(by=["Categoria", "Valor"], ascending=[True, True])

        # 3. Calculamos o total por Categoria para exibir fora da barra
        df_totais_cat = df_vendas.groupby("Categoria")["Valor"].sum().reset_index(name='Total')
        
        # Ordenamos as categorias para que a que mais faturou fique no topo
        cat_order = df_totais_cat.sort_values("Total", ascending=True)["Categoria"].tolist()

        # 4. Criamos o gráfico empilhado
        fig2 = px.bar(df_mix, x="Valor", y="Categoria", color="Canal_Agrupado",
                        orientation='h', title="Mix de Vendas (€)",
                        color_discrete_map=PALETA_MAP_DYNAMIC,
                        category_orders={"Categoria": cat_order},
                        barmode='stack')

        # 5. Adicionamos o Total (€) fora da barra
        mapa_totais_cat = dict(zip(df_totais_cat['Categoria'], df_totais_cat['Total']))

        for cat in mapa_totais_cat:
            valor_formatado = format_number(mapa_totais_cat[cat])
            fig2.add_annotation(
                x=mapa_totais_cat[cat],
                y=cat,
                text=f"€ {valor_formatado}",
                showarrow=False,
                xanchor='left',
                xshift=10,
                font=dict(color="white", size=11)
            )

        # 6. Limpeza visual e ajustes de estilo
        fig2.update_traces(texttemplate='') # Remove números de dentro dos pedaços
        
        # Margem no eixo X para o texto não cortar
        max_valor = df_totais_cat['Total'].max()
        fig2.update_xaxes(range=[0, max_valor * 1.3])
        
        st.plotly_chart(estilo(fig2, show_x=False), use_container_width=True, config=conf)
    with c3:
        # C3 - SEM RÓTULOS (TEXTO)
        df_idade_qtd = df_vendas.groupby(["Faixa Etária", "Canal_Agrupado"]).size().reset_index(name='Qtd')
        fig3 = px.bar(df_idade_qtd, x="Faixa Etária", y="Qtd",
                      color="Canal_Agrupado", barmode='group',
                      title="Vendas por Idade", color_discrete_map=PALETA_MAP_DYNAMIC)
        st.plotly_chart(estilo(fig3, integer_y=True), use_container_width=True, config=conf)

    c4, c5, c6 = st.columns(3)
    with c4:
        # 1. Agrupamos os dados por País e Canal
        df_pais = df_vendas.groupby(["País", "Canal_Agrupado"]).size().reset_index(name='Qtd')
        
        # 2. Ordenação para o empilhamento (Menor na esquerda, Maior na direita)
        df_pais = df_pais.sort_values(by=["País", "Qtd"], ascending=[True, True])

        # 3. Calculamos o total por país para exibir fora da barra
        df_totais = df_vendas.groupby("País").size().reset_index(name='Total')
        
        # Definimos a ordem dos países pelo volume total (Ranking)
        pais_order = df_totais.sort_values("Total", ascending=False)["País"].tolist()

        # 4. Criamos o gráfico
        fig4 = px.bar(df_pais, y="País", x="Qtd", color="Canal_Agrupado",
                      barmode='stack', orientation='h', title="Clientes por País",
                      color_discrete_map=PALETA_MAP_DYNAMIC, 
                      category_orders={"País": pais_order})

        # 5. ADICIONAR O TOTAL FORA DA BARRA
        # Criamos um dicionário para mapear o total de cada país rapidamente
        mapa_totais = dict(zip(df_totais['País'], df_totais['Total']))

        # Adicionamos os totais como anotações no final de cada barra combinada
        for pais in mapa_totais:
            fig4.add_annotation(
                x=mapa_totais[pais], # Posição X é o total
                y=pais,              # Posição Y é o nome do país
                text=str(mapa_totais[pais]), # O texto é o número total
                showarrow=False,
                xanchor='left',      # Alinha o texto à esquerda do ponto X (fica para fora)
                xshift=10,           # Empurra o texto 10 pixels para a direita da barra
                font=dict(color="white", size=12)
            )

        # 6. Ajustes de Estilo (Removi o texto de dentro para focar no total fora)
        fig4.update_traces(
            texttemplate='', # Remove números de dentro dos pedaços para não poluir
            hoverinfo='all'  # Mantém a info ao passar o mouse
        )

        # Ajuste do eixo X para dar espaço ao número do total
        max_total = df_totais['Total'].max()
        fig4.update_xaxes(range=[0, max_total * 1.3])
        
        st.plotly_chart(estilo(fig4, show_x=False, integer_x=True), use_container_width=True, config=conf)
    with c5:
        df_idade_valor = df_vendas.groupby(["Faixa Etária", "Canal_Agrupado"])["Valor"].sum().reset_index()
        fig5 = px.bar(df_idade_valor, x="Faixa Etária", y="Valor",
                      color="Canal_Agrupado", barmode='group',
                      title="Faturamento por Idade (€)", color_discrete_map=PALETA_MAP_DYNAMIC,
                      text=df_idade_valor["Valor"].apply(format_number))
        fig5.update_traces(textposition='outside')
        st.plotly_chart(estilo(fig5), use_container_width=True, config=conf)

    with c6:
        df_saldo = df_vendas[df_vendas['Saldo Total'] > 0].copy()
        if not df_saldo.empty:
            def treat_name(name):
                clean = str(name)
                return (clean[:15] + '..') if len(clean) > 16 else clean
            df_saldo['Cliente'] = df_saldo['Cliente'].apply(treat_name)
            df_saldo = df_saldo.sort_values("Saldo Total", ascending=False).head(5)
            fig6 = px.bar(df_saldo, y="Cliente", x="Saldo Total", color="Canal_Agrupado",
                          orientation='h', title="Top 5 Devedores (€)",
                          color_discrete_map=PALETA_MAP_DYNAMIC,
                          text=df_saldo["Saldo Total"].apply(format_number))
            fig6.update_traces(textposition='outside')
            fig6.update_xaxes(range=[0, df_saldo["Saldo Total"].max() * 1.3])
            st.plotly_chart(estilo(fig6, show_x=False), use_container_width=True, config=conf)

st.write(""); st.write("")