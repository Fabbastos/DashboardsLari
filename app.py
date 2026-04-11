import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Executive CRM", layout="wide")

# --- CORES IDENTIDADE ---
COLOR_LEAD, COLOR_KALIL, TEXT_COLOR = "#5BC0EB", "#A05195", "#FFFFFF"
PALETA_MAP = {"Lead": COLOR_LEAD, "Kalil": COLOR_KALIL}

# --- CSS RESPONSIVO E DESIGN ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0F172A; }}
    .block-container {{ padding: 0.2rem 1rem 5rem 1rem !important; }}
    header {{ visibility: hidden; height: 0px; }}
    footer {{ visibility: hidden; }}
    .stDeployButton {{ display:none; }}
    
    .main-title {{ font-size: 1.2rem !important; font-weight: bold; margin: 10px 0px !important; color: white; }}
    .channel-label {{ font-size: 1.1rem !important; font-weight: 800 !important; margin-bottom: 5px !important; border-bottom: 1px solid rgba(255,255,255,0.1); display: inline-block; width: 100%; }}

    div[data-testid="stMetric"] {{ background-color: #1E293B; padding: 2px 10px !important; border: 1px solid #334155; height: 50px !important; }}
    div[data-testid="stMetricLabel"] {{ font-size: 0.72rem !important; color: #CBD5E1 !important; margin-bottom: -15px; }}
    div[data-testid="stMetricValue"] {{ font-size: 1.0rem !important; font-weight: bold; color: white !important; }}

    hr {{ margin: 8px 0px !important; opacity: 0.1; }}
    div[data-testid="stSelectbox"] {{ margin-top: -10px; }}

    /* RESPONSIVIDADE PARA CELULAR */
    @media (max-width: 768px) {{
        [data-testid="column"] {{
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
            margin-bottom: 10px;
        }}
        div[data-testid="stMetric"] {{ height: 60px !important; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. Dados
def load_data():
    columns = ['Cliente', 'Canal', 'Categoria', 'Valor', 'Entrada', 'Idade', 'Segundo_Pagto', 'País', 'Mês']
    data = [
        ['Ana Silva', 'Lead', 'ID-DEFINITIVO', 5000, 5000, '20-25', 0, 'Brasil', 'Janeiro'],
        ['Bruno Costa', 'Kalil', 'TRC PROV.', 1500, 500, '31-35', 0, 'Portugal', 'Janeiro'],
        ['Carla Souza', 'Lead', 'AE TODAS', 4500, 4500, '40-45', 0, 'Brasil', 'Fevereiro'],
        ['Diego Lima', 'Kalil', 'AB CARRO', 8000, 4000, '31-35', 2000, 'Angola', 'Fevereiro'],
        ['Erik Rocha', 'Lead', 'Carta AE', 6000, 3000, '26-30', 1000, 'Brasil', 'Março'],
        ['Gabriel Mendes', 'Lead', 'ID-DEFINITIVO', 5200, 5200, '20-25', 0, 'Brasil', 'Janeiro'],
        ['Juliana Paes', 'Kalil', 'AB CARRO', 7500, 7500, '40-45', 0, 'EUA', 'Fevereiro'],
        ['Lucas Lima', 'Lead', 'Potencial', 0, 0, '26-30', 0, 'Brasil', 'Janeiro'],
        ['Mariana Rios', 'Lead', 'Potencial', 0, 0, '31-35', 0, 'Brasil', 'Janeiro'],
        ['Pedro Sales', 'Lead', 'Potencial', 0, 0, '20-25', 0, 'Portugal', 'Fevereiro'],
        ['Joana Dark', 'Kalil', 'Potencial', 0, 0, '40-45', 0, 'Angola', 'Janeiro'],
        ['Roberto Carlos', 'Kalil', 'Potencial', 0, 0, '50-55', 0, 'Brasil', 'Fevereiro'],
        ['Aline Moraes', 'Kalil', 'Potencial', 0, 0, '26-30', 0, 'Portugal', 'Março'],
        ['Vitor Kley', 'Lead', 'Potencial', 0, 0, '20-25', 0, 'Brasil', 'Março'],
    ]
    df = pd.DataFrame(data, columns=columns)
    df['Total Pago'] = df['Entrada'] + df['Segundo_Pagto']
    df['Saldo Total'] = df['Valor'] - df['Total Pago']
    df['Pago Vista'] = df.apply(lambda x: x['Valor'] if x['Entrada'] == x['Valor'] and x['Valor'] > 0 else 0, axis=1)
    df['Pago Parcelado'] = df.apply(lambda x: x['Total Pago'] if x['Entrada'] < x['Valor'] else 0, axis=1)
    df['Saldo Parcelado'] = df.apply(lambda x: x['Saldo Total'] if x['Entrada'] < x['Valor'] else 0, axis=1)
    return df

df_base = load_data()

# --- CABEÇALHO ---
head_col1, head_col2 = st.columns([4, 1])
with head_col1:
    st.markdown('<p class="main-title">📊 Executive CRM Dashboard</p>', unsafe_allow_html=True)
with head_col2:
    mes_filtro = st.selectbox("", ["Total", "Janeiro", "Fevereiro", "Março"], label_visibility="collapsed")

df = df_base if mes_filtro == "Total" else df_base[df_base['Mês'] == mes_filtro]
df_vendas = df[df['Total Pago'] > 0].copy()

# --- MÉTRICAS ---
def render_metrics(channel, color):
    subset = df[df['Canal'] == channel]
    st.markdown(f"<p class='channel-label' style='color:{color}'>{channel}</p>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Faturamento", f"R$ {subset['Valor'].sum():,.0f}")
    m2.metric("Pago à Vista", f"R$ {subset['Pago Vista'].sum():,.0f}")
    m3.metric("Pago Parcelado", f"R$ {subset['Pago Parcelado'].sum():,.0f}")
    m4.metric("Saldo Parcelado", f"R$ {subset['Saldo Parcelado'].sum():,.0f}")

render_metrics('Lead', COLOR_LEAD)
render_metrics('Kalil', COLOR_KALIL)
st.markdown("<hr>", unsafe_allow_html=True)

def aplicar_estilo_estatico(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=TEXT_COLOR, size=11), margin=dict(l=10, r=10, t=35, b=5), height=200,
        hovermode=False, # Desativa o hover no layout
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_traces(hoverinfo='none', textfont_color="white") # Remove info de passagem de mouse
    return fig

# --- GRÁFICOS (Com configuração de estático) ---
config_estatico = {'staticPlot': True}

c1, c2, c3 = st.columns(3)

with c1:
    funnel_rows = []
    for canal in ["Lead", "Kalil"]:
        canal_df = df[df['Canal'] == canal]
        funnel_rows.append({'Etapa': '1. Contatos', 'Canal': canal, 'Qtd': len(canal_df)})
        funnel_rows.append({'Etapa': '2. Clientes', 'Canal': canal, 'Qtd': len(canal_df[canal_df['Total Pago'] > 0])})
    fig1 = px.funnel(pd.DataFrame(funnel_rows), x='Qtd', y='Etapa', color='Canal', title="Funil de Vendas", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_estatico(fig1), use_container_width=True, config=config_estatico)

with c2:
    fig2 = px.bar(df_vendas.groupby("Categoria")["Valor"].sum().reset_index(), x="Valor", y="Categoria", orientation='h', title="Mix de Vendas (R$)", color_discrete_sequence=[COLOR_LEAD])
    st.plotly_chart(aplicar_estilo_estatico(fig2), use_container_width=True, config=config_estatico)

with c3:
    fig3 = px.bar(df_vendas.groupby(["Idade", "Canal"]).size().reset_index(name='Qtd'), x="Idade", y="Qtd", color="Canal", barmode='group', title="Qtd. Vendas por Idade", color_discrete_map=PALETA_MAP)
    fig3.update_xaxes(categoryorder='category ascending')
    st.plotly_chart(aplicar_estilo_estatico(fig3), use_container_width=True, config=config_estatico)

c4, c5, c6 = st.columns(3)

with c4:
    fig4 = px.bar(df_vendas.groupby(["País", "Canal"]).size().reset_index(name='Qtd'), x="País", y="Qtd", color="Canal", barmode='group', title="Clientes por País", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_estatico(fig4), use_container_width=True, config=config_estatico)

with c5:
    fig5 = px.bar(df_vendas.groupby(["Idade", "Canal"])["Valor"].sum().reset_index(), x="Idade", y="Valor", color="Canal", barmode='group', title="Faturamento por Idade", color_discrete_map=PALETA_MAP)
    fig5.update_xaxes(categoryorder='category ascending')
    st.plotly_chart(aplicar_estilo_estatico(fig5), use_container_width=True, config=config_estatico)

with c6:
    fig6 = px.bar(df_vendas[df_vendas['Saldo Total'] > 0], x="Cliente", y="Saldo Total", color="Canal", title="Saldo Devedor por Cliente", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_estatico(fig6), use_container_width=True, config=config_estatico)

st.write(""); st.write("")