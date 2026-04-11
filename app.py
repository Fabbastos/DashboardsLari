import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Executive CRM", layout="wide", page_icon="📊")

# --- CSS: Contraste Máximo e Layout sem Rolagem ---
st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #FFFFFF; }
    
    /* Forçar títulos e textos globais para branco */
    h1, h2, h3, p, span, label, .stMarkdown { color: #FFFFFF !important; }
    
    /* Remover espaços e margens para caber na tela */
    .block-container { padding: 1rem 2rem !important; }
    
    /* Cards de Métricas */
    div[data-testid="stMetric"] {
        background-color: #1E293B;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #334155;
    }
    div[data-testid="stMetricLabel"] { color: #94A3B8 !important; }
    div[data-testid="stMetricValue"] { color: #5BC0EB !important; font-size: 1.8rem !important; }

    /* Esconder elementos nativos do Streamlit */
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# 2. Dados de Exemplo (Mantendo sua estrutura)
def load_data():
    columns = ['Cliente', 'Indicador', 'Categoria', 'Valor', 'Entrada', 'Idade', 'Segundo_Pagto', 'País', 'Doc_Status']
    data = [
        ['Ana Silva', 'Instagram', 'ID-DEFINITIVO', 5000, 2500, '20-25', 1000, 'Brasil', 'Ok'],
        ['Bruno Costa', 'Kalil', 'TRC PROVISÓRIO', 1500, 500, '30-35', 0, 'Portugal', 'Pendente'],
        ['Carla Souza', 'Google', 'AE TODAS', 4500, 4500, '40-45', 0, 'Brasil', 'Ok'],
        ['Diego Lima', 'Kalil', 'AB CARRO', 8000, 4000, '30-35', 2000, 'Angola', 'Pendente'],
        ['Erik Rocha', 'Instagram', 'Carta AE', 6000, 3000, '25-30', 1000, 'Brasil', 'Ok'],
        ['Fernanda Luz', 'Google', 'Renov. CNH', 1200, 1200, '50-55', 0, 'Portugal', 'Ok'],
    ]
    return pd.DataFrame(data, columns=columns)

df = load_data()
df['Total Pago'] = df['Entrada'] + df['Segundo_Pagto']
df['Saldo'] = df['Valor'] - df['Total Pago']

# 3. Cabeçalho e Métricas
st.title("📊 Executive CRM Dashboard")

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Faturamento", f"R$ {df['Valor'].sum():,.0f}")
m2.metric("Recebido", f"R$ {df['Total Pago'].sum():,.0f}")
m3.metric("Saldo", f"R$ {df['Saldo'].sum():,.0f}")
m4.metric("Vendas", len(df))
m5.metric("Ticket Médio", f"R$ {df['Valor'].mean():,.0f}")
m6.metric("LTV", "R$ 4.2k")

# --- Configuração de Estilo dos Gráficos ---
cores = ["#5BC0EB", "#A05195", "#F9B24D", "#2F5D8C", "#665191"]
chart_height = 200 # Altura ideal para 2 fileiras de gráficos sem scroll

def aplicar_estilo_dark(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white", size=11), # LETRA BRANCA NOS EIXOS
        title_font=dict(color="white", size=14),
        margin=dict(l=10, r=10, t=40, b=10),
        height=chart_height
    )
    fig.update_xaxes(gridcolor='#334155', zerolinecolor='#334155')
    fig.update_yaxes(gridcolor='#334155', zerolinecolor='#334155')
    return fig

# 4. Primeira Fileira de Gráficos (3 colunas)
st.write("") # Espaçador
c1, c2, c3 = st.columns(3)

with c1:
    fig1 = px.bar(df.groupby("Indicador")["Valor"].sum().reset_index(), 
                  x="Valor", y="Indicador", orientation='h', title="Vendas por Canal",
                  color_discrete_sequence=[cores[0]])
    st.plotly_chart(aplicar_estilo_dark(fig1), use_container_width=True)

with c2:
    fig2 = px.pie(df, values='Valor', names='Categoria', hole=.5, title="Mix de Produtos")
    fig2.update_traces(marker=dict(colors=cores))
    fig2.update_layout(showlegend=False)
    st.plotly_chart(aplicar_estilo_dark(fig2), use_container_width=True)

with c3:
    fig3 = px.bar(df.groupby("Idade")["Valor"].sum().reset_index(), 
                  x="Idade", y="Valor", title="Faturamento por Idade",
                  color_discrete_sequence=[cores[1]])
    st.plotly_chart(aplicar_estilo_dark(fig3), use_container_width=True)

# 5. Segunda Fileira de Gráficos (Mais 3 Gráficos no lugar da tabela)
c4, c5, c6 = st.columns(3)

with c4:
    # Gráfico de Países
    fig4 = px.bar(df.groupby("País")["Valor"].count().reset_index(), 
                  x="País", y="Valor", title="Vendas por País",
                  color_discrete_sequence=[cores[2]])
    st.plotly_chart(aplicar_estilo_dark(fig4), use_container_width=True)

with c5:
    # Status de Documentos (Donut)
    fig5 = px.pie(df, names='Doc_Status', title="Status de Documentação", hole=.5)
    fig5.update_traces(marker=dict(colors=["#27ae60", "#e74c3c"]))
    fig5.update_layout(showlegend=False)
    st.plotly_chart(aplicar_estilo_dark(fig5), use_container_width=True)

with c6:
    # Saldo a Receber por Cliente
    fig6 = px.bar(df, x="Cliente", y="Saldo", title="Saldo Devedor p/ Cliente",
                  color_discrete_sequence=["#F9B24D"])
    st.plotly_chart(aplicar_estilo_dark(fig6), use_container_width=True)