import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Executive CRM", layout="wide", page_icon="📊")

# --- Cores Identidade Visual ---
COLOR_LEAD = "#5BC0EB" # Azul
COLOR_KALIL = "#A05195" # Roxo
TEXT_COLOR = "#FFFFFF"
PALETA_MAP = {"Lead": COLOR_LEAD, "Kalil": COLOR_KALIL}

# --- CSS: Otimização Extrema de Espaço ---
st.markdown(f"""
    <style>
    /* Remove margens do container principal */
    .block-container {{ 
        padding-top: 0.5rem !important; 
        padding-bottom: 0rem !important; 
        padding-left: 1rem !important; 
        padding-right: 1rem !important; 
    }}
    /* Reduz a altura dos cards de métricas */
    div[data-testid="stMetric"] {{
        background-color: #1E293B;
        padding: 5px 10px !important;
        border-radius: 8px;
        border: 1px solid #334155;
    }}
    /* Esconde o cabeçalho padrão do Streamlit para ganhar espaço */
    header {{ visibility: hidden; height: 0px; }}
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
chart_height = 260

# --- Ajuste na Função de Estilo ---
def aplicar_estilo_dark(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=TEXT_COLOR, size=11), # Fonte levemente menor
        title_font=dict(color=TEXT_COLOR, size=14, family="Arial Black"),
        # Margens negativas ou zero para aproveitar cada pixel
        margin=dict(l=5, r=5, t=35, b=5), 
        height=220, # Reduzi de 260 para 220 para caber na tela
        legend=dict(
            font=dict(size=10),
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1
        )
    )
    fig.update_xaxes(gridcolor='#1E293B', tickfont=dict(size=10))
    fig.update_yaxes(gridcolor='#1E293B', tickfont=dict(size=10))
    fig.update_traces(textfont_size=11)
    return fig

# 4. Cabeçalho e Métricas
st.markdown("<h2 style='margin-bottom: 20px;'>📊 Executive CRM Dashboard</h2>", unsafe_allow_html=True)

fat_lead = df[df['Canal'] == 'Lead']['Valor'].sum()
fat_kalil = df[df['Canal'] == 'Kalil']['Valor'].sum()

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Faturamento LEAD", f"R$ {fat_lead:,.0f}")
m2.metric("Faturamento KALIL", f"R$ {fat_kalil:,.0f}")
m3.metric("Total Recebido", f"R$ {df['Total Pago'].sum():,.0f}")
m4.metric("Saldo a Receber", f"R$ {df['Saldo'].sum():,.0f}")
m5.metric("Ticket Médio", f"R$ {df['Valor'].mean():,.0f}")

# 5. Gráficos
st.write("---")
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
                  title="Mix de Produtos", color_discrete_sequence=[COLOR_LEAD])
    st.plotly_chart(aplicar_estilo_dark(fig2), use_container_width=True)

with c3:
    fig3 = px.bar(df.groupby(["Idade", "Canal"])["Valor"].sum().reset_index(), 
                  x="Idade", y="Valor", color="Canal", barmode='group',
                  title="Faturamento por Idade", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_dark(fig3), use_container_width=True)

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
                  title="Saldo Devedor por Cliente", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_dark(fig6), use_container_width=True)