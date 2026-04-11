import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração
st.set_page_config(page_title="Executive CRM", layout="wide")

# --- CORES ---
COLOR_LEAD, COLOR_KALIL, TEXT_COLOR = "#5BC0EB", "#A05195", "#FFFFFF"
PALETA_MAP = {"Lead": COLOR_LEAD, "Kalil": COLOR_KALIL}

# --- CSS REFINADO ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0F172A; }}
    .block-container {{ padding: 0.5rem 1rem !important; }}
    header, footer {{ visibility: hidden; height: 0px; }}
    
    .main-title {{ 
        font-size: 1.4rem !important; 
        font-weight: bold; 
        margin-bottom: 15px !important; 
        color: white;
    }}
    
    /* Cards de Métricas */
    div[data-testid="stMetric"] {{
        background-color: #1E293B;
        padding: 5px 12px !important;
        border: 1px solid #334155;
        height: 70px;
        margin-bottom: 5px !important;
    }}
    div[data-testid="stMetricLabel"] {{ font-size: 0.85rem !important; color: #CBD5E1 !important; }}
    div[data-testid="stMetricValue"] {{ font-size: 1.3rem !important; font-weight: bold; color: white !important; }}

    hr {{ margin: 1rem 0rem !important; opacity: 0.1; }}
    </style>
    """, unsafe_allow_html=True)

# 2. Dados
def load_data():
    columns = ['Cliente', 'Canal', 'Categoria', 'Valor', 'Entrada', 'Idade', 'Segundo_Pagto', 'País', 'Doc_Status']
    data = [
        ['Ana Silva', 'Lead', 'ID-DEFINITIVO', 5000, 2500, '20-25', 1000, 'Brasil', 'Ok'],
        ['Bruno Costa', 'Kalil', 'TRC PROV.', 1500, 500, '30-35', 0, 'Portugal', 'Pendente'],
        ['Carla Souza', 'Lead', 'AE TODAS', 4500, 4500, '40-45', 0, 'Brasil', 'Ok'],
        ['Diego Lima', 'Kalil', 'AB CARRO', 8000, 4000, '30-35', 2000, 'Angola', 'Pendente'],
        ['Erik Rocha', 'Lead', 'Carta AE', 6000, 3000, '25-30', 1000, 'Brasil', 'Ok'],
        ['Fernanda Luz', 'Lead', 'Renov. CNH', 1200, 1200, '50-55', 0, 'Portugal', 'Ok'],
    ]
    df = pd.DataFrame(data, columns=columns)
    df['Total Pago'] = df['Entrada'] + df['Segundo_Pagto']
    df['Saldo'] = df['Valor'] - df['Total Pago']
    return df

df = load_data()

# --- FUNÇÃO DE ESTILO COM FONTES AMPLIADAS ---
def aplicar_estilo_legivel(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        # Aumentei a fonte base de 10 para 13
        font=dict(color=TEXT_COLOR, size=13),
        title_font=dict(color=TEXT_COLOR, size=16, family="Arial Black"),
        margin=dict(l=10, r=10, t=40, b=10),
        height=220, 
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=12))
    )
    # Eixos com fontes maiores e mais nítidas
    fig.update_xaxes(title="", gridcolor='#1E293B', tickfont=dict(size=12, color="#FFFFFF"))
    fig.update_yaxes(title="", gridcolor='#1E293B', tickfont=dict(size=12, color="#FFFFFF"))
    # Força rótulos de dados (labels) a ficarem maiores
    fig.update_traces(textfont_size=13)
    return fig

# 3. Layout
st.markdown('<p class="main-title">📊 Executive CRM Dashboard</p>', unsafe_allow_html=True)

# --- Cálculos Segmentados ---
def get_metrics(channel):
    subset = df[df['Canal'] == channel]
    return {
        "fat": subset['Valor'].sum(),
        "pago": subset['Total Pago'].sum(),
        "saldo": subset['Saldo'].sum(),
        "ticket": subset['Valor'].mean() if len(subset) > 0 else 0
    }

lead_m = get_metrics('Lead')
kalil_m = get_metrics('Kalil')

# --- Layout de Métricas em Linhas ---
st.markdown('<p class="main-title">📊 Executive CRM Dashboard</p>', unsafe_allow_html=True)

# LINHA 1: LEAD (Azul)
st.markdown("<p style='margin-bottom: -10px; color: #5BC0EB; font-weight: bold; font-size: 0.9rem;'>PERFORMANCE LEAD</p>", unsafe_allow_html=True)
l1, l2, l3, l4 = st.columns(4)
l1.metric("Faturamento", f"R$ {lead_m['fat']:,.0f}")
l2.metric("Total Pago", f"R$ {lead_m['pago']:,.0f}")
l3.metric("Saldo a Pagar", f"R$ {lead_m['saldo']:,.0f}")
l4.metric("Ticket Médio", f"R$ {lead_m['ticket']:,.0f}")

# Espaçador fino entre as linhas
st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)

# LINHA 2: KALIL (Roxo)
st.markdown("<p style='margin-bottom: -10px; color: #A05195; font-weight: bold; font-size: 0.9rem;'>PERFORMANCE KALIL</p>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
k1.metric("Faturamento", f"R$ {kalil_m['fat']:,.0f}")
k2.metric("Total Pago", f"R$ {kalil_m['pago']:,.0f}")
k3.metric("Saldo a Pagar", f"R$ {kalil_m['saldo']:,.0f}")
k4.metric("Ticket Médio", f"R$ {kalil_m['ticket']:,.0f}")

st.markdown("---")

# --- Gráficos ---
c1, c2, c3 = st.columns(3)
with c1:
    df_funil = pd.DataFrame({'Etapa':['Contatos','Vendas','Contatos','Vendas'],'Canal':['Lead','Lead','Kalil','Kalil'],'Qtd':[40,4,12,2]})
    fig1 = px.funnel(df_funil, x='Qtd', y='Etapa', color='Canal', title="Conversão", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_legivel(fig1), use_container_width=True)

with c2:
    fig2 = px.bar(df.groupby("Categoria")["Valor"].sum().reset_index(), x="Valor", y="Categoria", orientation='h', title="Mix de Produtos", color_discrete_sequence=[COLOR_LEAD])
    st.plotly_chart(aplicar_estilo_legivel(fig2), use_container_width=True)

with c3:
    fig3 = px.bar(df.groupby(["Idade", "Canal"])["Valor"].sum().reset_index(), x="Idade", y="Valor", color="Canal", barmode='group', title="Idade por Canal", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_legivel(fig3), use_container_width=True)

c4, c5, c6 = st.columns(3)
with c4:
    fig4 = px.bar(df.groupby(["País", "Canal"])["Valor"].sum().reset_index(), x="País", y="Valor", color="Canal", title="País", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_legivel(fig4), use_container_width=True)

with c5:
    fig5 = px.bar(df.groupby(["Doc_Status", "Canal"])["Valor"].count().reset_index(), x="Valor", y="Doc_Status", color="Canal", orientation='h', title="Documentação", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_legivel(fig5), use_container_width=True)

with c6:
    fig6 = px.bar(df[df['Saldo'] > 0], x="Cliente", y="Saldo", color="Canal", title="Saldo Devedor Detalhado", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_legivel(fig6), use_container_width=True)