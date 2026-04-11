import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. Configuração da Página
st.set_page_config(page_title="Executive CRM", layout="wide")

# --- CORES IDENTIDADE ---
COLOR_LEAD, COLOR_KALIL, TEXT_COLOR = "#5BC0EB", "#A05195", "#FFFFFF"
PALETA_MAP = {"Lead": COLOR_LEAD, "Kalil": COLOR_KALIL}

# --- CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0F172A; }}
    .block-container {{ padding: 0.2rem 1rem 0rem 1rem !important; }}
    header {{ visibility: hidden; height: 0px; }}
    footer {{ visibility: hidden; }}
    .stDeployButton {{ display:none; }}
    
    .main-title {{ font-size: 1.2rem !important; font-weight: bold; margin-bottom: 10px !important; color: white; }}
    .channel-label {{ font-size: 1.1rem !important; font-weight: 800 !important; margin: 5px 0px; letter-spacing: 1px; text-transform: uppercase; border-bottom: 1px solid rgba(255,255,255,0.1); width: 100%; }}

    div[data-testid="stMetric"] {{ background-color: #1E293B; padding: 2px 10px !important; border: 1px solid #334155; height: 50px !important; margin-bottom: 2px !important; }}
    div[data-testid="stMetricLabel"] {{ font-size: 0.72rem !important; color: #CBD5E1 !important; margin-bottom: -15px; }}
    div[data-testid="stMetricValue"] {{ font-size: 1.0rem !important; font-weight: bold; color: white !important; }}
    hr {{ margin: 8px 0px !important; opacity: 0.1; }}
    </style>
    """, unsafe_allow_html=True)

# 2. Gestão de Dados (Utilizando session_state para permitir adição)
if 'db' not in st.session_state:
    data = [
        ['Ana Silva', 'Lead', 'ID-DEFINITIVO', 5000, 5000, '20-25', 0, 'Brasil', 'Janeiro'],
        ['Bruno Costa', 'Kalil', 'TRC PROV.', 1500, 500, '31-35', 0, 'Portugal', 'Janeiro'],
        ['Diego Lima', 'Kalil', 'AB CARRO', 8000, 4000, '31-35', 2000, 'Angola', 'Fevereiro'],
        ['Erik Rocha', 'Lead', 'Carta AE', 6000, 3000, '26-30', 1000, 'Brasil', 'Fevereiro'],
        ['Gabriel Mendes', 'Lead', 'ID-DEFINITIVO', 5200, 5200, '20-25', 0, 'Brasil', 'Março'],
        ['Helena Ramos', 'Kalil', 'TRC PROV.', 1800, 0, '26-30', 0, 'Portugal', 'Março'], # Contato (Valor pago = 0)
        ['Igor Antunes', 'Lead', 'AE TODAS', 4500, 0, '31-35', 0, 'Angola', 'Março'],    # Contato (Valor pago = 0)
    ]
    st.session_state.db = pd.DataFrame(data, columns=['Cliente', 'Canal', 'Categoria', 'Valor', 'Entrada', 'Idade', 'Segundo_Pagto', 'País', 'Mês'])

# --- SIDEBAR: ADICIONAR CONTATOS ---
with st.sidebar:
    st.title("Novo Lead")
    with st.form("form_contato"):
        novo_nome = st.text_input("Nome do Cliente")
        novo_canal = st.selectbox("Canal", ["Lead", "Kalil"])
        novo_pais = st.selectbox("País", ["Brasil", "Portugal", "Angola", "EUA"])
        novo_mes = st.selectbox("Mês", ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho"])
        # Se for apenas contato, Valor e Entrada serão 0 inicialmente
        if st.form_submit_button("Cadastrar como Potencial"):
            nova_linha = pd.DataFrame([[novo_nome, novo_canal, "Lead Novo", 0, 0, "N/A", 0, novo_pais, novo_mes]], 
                                      columns=st.session_state.db.columns)
            st.session_state.db = pd.concat([st.session_state.db, nova_linha], ignore_index=True)
            st.success("Lead adicionado!")

    st.markdown("---")
    meses_selecionados = st.multiselect("Filtrar Meses", options=st.session_state.db['Mês'].unique(), default=st.session_state.db['Mês'].unique())

# --- PROCESSAMENTO ---
df_filtered = st.session_state.db[st.session_state.db['Mês'].isin(meses_selecionados)].copy()
df_filtered['Total Pago'] = df_filtered['Entrada'] + df_filtered['Segundo_Pagto']
df_filtered['Saldo Total'] = df_filtered['Valor'] - df_filtered['Total Pago']
df_filtered['Status'] = df_filtered['Total Pago'].apply(lambda x: 'Cliente' if x > 0 else 'Contato')

# 3. Layout Principal
st.markdown('<p class="main-title">📊 Executive CRM Dashboard</p>', unsafe_allow_html=True)

def render_metrics(channel, color):
    subset = df_filtered[df_filtered['Canal'] == channel]
    st.markdown(f"<p class='channel-label' style='color:{color}'>{channel}</p>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Faturamento", f"R$ {subset['Valor'].sum():,.0f}")
    m2.metric("Total Pago", f"R$ {subset['Total Pago'].sum():,.0f}")
    m3.metric("Saldo Total", f"R$ {subset['Saldo Total'].sum():,.0f}")
    m4.metric("Contatos Ativos", len(subset))

render_metrics('Lead', COLOR_LEAD)
render_metrics('Kalil', COLOR_KALIL)

def aplicar_estilo_dashboard(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=TEXT_COLOR, size=11), margin=dict(l=10, r=10, t=35, b=5), height=200,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_traces(textfont_color="white")
    return fig

st.markdown("<hr>", unsafe_allow_html=True)

# --- GRÁFICOS ---
c1, c2, c3 = st.columns(3)

with c1:
    # FUNIL REAL: Conta quantos são "Contatos" (todos) e quantos viraram "Clientes" (pagaram > 0)
    funnel_data = []
    for canal in ["Lead", "Kalil"]:
        total_leads = len(df_filtered[df_filtered['Canal'] == canal])
        total_clientes = len(df_filtered[(df_filtered['Canal'] == canal) & (df_filtered['Status'] == 'Cliente')])
        funnel_data.append({'Etapa': 'Total Leads', 'Canal': canal, 'Qtd': total_leads})
        funnel_data.append({'Etapa': 'Vendas', 'Canal': canal, 'Qtd': total_clientes})
    
    fig1 = px.funnel(pd.DataFrame(funnel_data), x='Qtd', y='Etapa', color='Canal', title="Funil de Conversão Real", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_dashboard(fig1), use_container_width=True)

with c2:
    fig2 = px.bar(df_filtered[df_filtered['Valor'] > 0].groupby("Categoria")["Valor"].sum().reset_index(), x="Valor", y="Categoria", orientation='h', title="Mix de Produtos (R$)", color_discrete_sequence=[COLOR_LEAD])
    st.plotly_chart(aplicar_estilo_dashboard(fig2), use_container_width=True)

with c3:
    fig3 = px.bar(df_filtered.groupby(["País", "Canal"]).size().reset_index(name='Qtd'), x="País", y="Qtd", color="Canal", barmode='group', title="Clientes por País", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_dashboard(fig3), use_container_width=True)

# Tabela de Novos Leads/Contatos para acompanhamento
st.markdown("<p class='channel-label'>Lista de Leads e Potenciais Clientes</p>", unsafe_allow_html=True)
st.dataframe(df_filtered[['Cliente', 'Canal', 'País', 'Mês', 'Status', 'Valor', 'Saldo Total']], use_container_width=True)