import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Executive CRM", layout="wide", page_icon="📊")

# --- Cores Identidade Visual ---
COLOR_LEAD = "#5BC0EB" # Azul
COLOR_KALIL = "#A05195" # Roxo
PALETA_MAP = {"Lead": COLOR_LEAD, "Kalil": COLOR_KALIL}

# --- CSS: Otimização de Espaço e Cores ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0F172A; color: #FFFFFF; }}
    .block-container {{ padding-top: 0.5rem !important; padding-bottom: 0rem !important; }}
    #MainMenu, footer, header {{ display: none !important; }}
    
    div[data-testid="stMetric"] {{
        background-color: #1E293B;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #334155;
    }}
    div[data-testid="stMetricLabel"] {{ color: #CBD5E1 !important; font-size: 0.9rem !important; }}
    div[data-testid="stMetricValue"] {{ color: #FFFFFF !important; font-size: 1.5rem !important; font-weight: bold; }}
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
    return pd.DataFrame(data, columns=columns)

df = load_data()
df['Total Pago'] = df['Entrada'] + df['Segundo_Pagto']
df['Saldo'] = df['Valor'] - df['Total Pago']
chart_height = 240

# 3. Funções de Estilo
def aplicar_estilo_dark(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#FFFFFF", size=12),
        title_font=dict(color="#FFFFFF", size=15, family="Arial Black"),
        margin=dict(l=10, r=10, t=40, b=10),
        height=chart_height,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_xaxes(gridcolor='#1E293B', zerolinecolor='#1E293B')
    fig.update_yaxes(gridcolor='#1E293B', zerolinecolor='#1E293B')
    return fig

# 4. Cabeçalho e Métricas
st.markdown("<h2 style='margin-bottom: 20px;'>📊 Executive CRM Dashboard</h2>", unsafe_allow_html=True)

fat_lead = df[df['Canal'] == 'Lead']['Valor'].sum()
fat_kalil = df[df['Canal'] == 'Kalil']['Valor'].sum()
ticket_medio = df['Valor'].mean()
vencedor = "Lead" if fat_lead > fat_kalil else "Kalil"

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Faturamento LEAD", f"R$ {fat_lead:,.0f}")
m2.metric("Faturamento KALIL", f"R$ {fat_kalil:,.0f}")
m3.metric("Total Recebido", f"R$ {df['Total Pago'].sum():,.0f}")
m4.metric("Saldo a Receber", f"R$ {df['Saldo'].sum():,.0f}")
m5.metric("Ticket Médio", f"R$ {ticket_medio:,.0f}") # Alterado para Ticket Médio
m6.metric(f"Vantagem ({vencedor})", f"R$ {abs(fat_lead - fat_kalil):,.0f}")

# 5. Fileira 1
c1, c2, c3 = st.columns(3)

with c1:
    df_funil = pd.DataFrame({
        'Etapa': ['1. Contatos', '2. Vendas', '1. Contatos', '2. Vendas'],
        'Origem': ['Lead', 'Lead', 'Kalil', 'Kalil'],
        'Qtd': [40, len(df[df['Canal'] == 'Lead']), 12, len(df[df['Canal'] == 'Kalil'])] 
    })
    fig1 = px.funnel(df_funil, x='Qtd', y='Etapa', color='Origem', 
                     title="Conversão por Canal", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_dark(fig1), use_container_width=True)

with c2:
    df_cat = df.groupby("Categoria")["Valor"].sum().reset_index().sort_values("Valor")
    fig2 = px.bar(df_cat, x="Valor", y="Categoria", orientation='h', 
                  title="Mix de Produtos", color_discrete_sequence=[COLOR_LEAD]) # Cor neutra ou destaque
    st.plotly_chart(aplicar_estilo_dark(fig2), use_container_width=True)

with c3:
    fig3 = px.bar(df.groupby(["Idade", "Canal"])["Valor"].sum().reset_index(), 
                  x="Idade", y="Valor", color="Canal", barmode='group',
                  title="Faturamento por Idade", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_dark(fig3), use_container_width=True)

# 6. Fileira 2
c4, c5, c6 = st.columns(3)

with c4:
    fig4 = px.bar(df.groupby(["País", "Canal"])["Valor"].sum().reset_index(), 
                  x="País", y="Valor", color="Canal", 
                  title="Faturamento por País", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_dark(fig4), use_container_width=True)

with c5:
    fig5 = px.bar(df.groupby(["Doc_Status", "Canal"])["Valor"].count().reset_index(), 
                  x="Valor", y="Doc_Status", color="Canal", orientation='h', 
                  title="Docs por Canal", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_dark(fig5), use_container_width=True)

with c6:
    fig6 = px.bar(df[df['Saldo'] > 0], x="Cliente", y="Saldo", color="Canal", 
                  title="Saldo Devedor", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_dark(fig6), use_container_width=True)