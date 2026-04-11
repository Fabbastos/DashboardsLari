import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Executive CRM", layout="wide")

# --- CORES E CONFIGS ---
COLOR_LEAD, COLOR_KALIL, TEXT_COLOR = "#5BC0EB", "#A05195", "#FFFFFF"
PALETA_MAP = {"Lead": COLOR_LEAD, "Kalil": COLOR_KALIL}

# --- CSS ULTRA COMPACTO ---
st.markdown(f"""
    <style>
    /* Remove todos os espaçamentos desnecessários */
    .block-container {{ padding: 0rem 1rem !important; }}
    header, footer {{ visibility: hidden; height: 0px; }}
    
    /* Título menor e colado no topo */
    .main-title {{ font-size: 1.2rem !important; font-weight: bold; margin: 0px 0px 5px 0px; }}
    
    /* Metrics compactas: Valor e Label na mesma linha ou muito próximos */
    div[data-testid="stMetric"] {{
        background-color: #1E293B;
        padding: 2px 10px !important;
        border: 1px solid #334155;
        height: 60px; /* Altura fixa baixa */
    }}
    div[data-testid="stMetricLabel"] {{ font-size: 0.75rem !important; margin-bottom: -10px; }}
    div[data-testid="stMetricValue"] {{ font-size: 1.1rem !important; }}
    
    /* Remove o espaço entre as colunas e os gráficos */
    .element-container, .stPlotlyChart {{ margin-bottom: -10px !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- DADOS (Simplificados para o exemplo) ---
def load_data():
    columns = ['Cliente', 'Canal', 'Categoria', 'Valor', 'Entrada', 'Idade', 'Segundo_Pagto', 'País', 'Doc_Status']
    data = [['Ana Silva', 'Lead', 'ID-DEFINITIVO', 5000, 2500, '20-25', 1000, 'Brasil', 'Ok'],
            ['Bruno Costa', 'Kalil', 'TRC PROV.', 1500, 500, '30-35', 0, 'Portugal', 'Pendente'],
            ['Carla Souza', 'Lead', 'AE TODAS', 4500, 4500, '40-45', 0, 'Brasil', 'Ok'],
            ['Diego Lima', 'Kalil', 'AB CARRO', 8000, 4000, '30-35', 2000, 'Angola', 'Pendente'],
            ['Erik Rocha', 'Lead', 'Carta AE', 6000, 3000, '25-30', 1000, 'Brasil', 'Ok'],
            ['Fernanda Luz', 'Lead', 'Renov. CNH', 1200, 1200, '50-55', 0, 'Portugal', 'Ok']]
    return pd.DataFrame(data, columns=columns)

df = load_data()
df['Total Pago'] = df['Entrada'] + df['Segundo_Pagto']
df['Saldo'] = df['Valor'] - df['Total Pago']

# --- FUNÇÃO DE ESTILO "TIGHT" ---
def aplicar_estilo_compacto(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=TEXT_COLOR, size=10),
        title_font=dict(color=TEXT_COLOR, size=12),
        margin=dict(l=5, r=5, t=30, b=5), # Margens mínimas
        height=190, # Altura mínima para não achatar os dados
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=0.95, xanchor="right", x=1, font=dict(size=9))
    )
    # Remove títulos dos eixos para ganhar espaço (o título do gráfico já explica)
    fig.update_xaxes(title="", gridcolor='#1E293B', tickfont=dict(size=9))
    fig.update_yaxes(title="", gridcolor='#1E293B', tickfont=dict(size=9))
    return fig

# --- LAYOUT ---
st.markdown('<p class="main-title">📊 Executive CRM Dashboard</p>', unsafe_allow_html=True)

# 5 Métricas em uma linha
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Faturamento LEAD", f"R$ {df[df['Canal']=='Lead']['Valor'].sum():,.0f}")
m2.metric("Faturamento KALIL", f"R$ {df[df['Canal']=='Kalil']['Valor'].sum():,.0f}")
m3.metric("Total Recebido", f"R$ {df['Total Pago'].sum():,.0f}")
m4.metric("Saldo a Receber", f"R$ {df['Saldo'].sum():,.0f}")
m5.metric("Ticket Médio", f"R$ {df['Valor'].mean():,.0f}")

st.markdown("---") # Linha divisória fina

# Duas fileiras de 3 gráficos
c1, c2, c3 = st.columns(3)
with c1:
    fig1 = px.funnel(pd.DataFrame({'Etapa':['Contatos','Vendas','Contatos','Vendas'],'Canal':['Lead','Lead','Kalil','Kalil'],'Qtd':[40,4,12,2]}), 
                     x='Qtd', y='Etapa', color='Canal', title="Conversão", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_compacto(fig1), use_container_width=True)
with c2:
    fig2 = px.bar(df.groupby("Categoria")["Valor"].sum().reset_index(), x="Valor", y="Categoria", orientation='h', title="Mix", color_discrete_sequence=[COLOR_LEAD])
    st.plotly_chart(aplicar_estilo_compacto(fig2), use_container_width=True)
with c3:
    fig3 = px.bar(df.groupby(["Idade", "Canal"])["Valor"].sum().reset_index(), x="Idade", y="Valor", color="Canal", barmode='group', title="Idade", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_compacto(fig3), use_container_width=True)

c4, c5, c6 = st.columns(3)
with c4:
    fig4 = px.bar(df.groupby(["País", "Canal"])["Valor"].sum().reset_index(), x="País", y="Valor", color="Canal", title="País", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_compacto(fig4), use_container_width=True)
with c5:
    fig5 = px.bar(df.groupby(["Doc_Status", "Canal"])["Valor"].count().reset_index(), x="Valor", y="Doc_Status", color="Canal", orientation='h', title="Docs", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_compacto(fig5), use_container_width=True)
with c6:
    fig6 = px.bar(df[df['Saldo'] > 0], x="Cliente", y="Saldo", color="Canal", title="Inadimplência", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_compacto(fig6), use_container_width=True)