import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="CRM Premium", layout="wide", page_icon="📊")

# --- Estilização CSS para Contraste e Espaçamento ---
st.markdown("""
    <style>
    /* Reset de cores para texto claro em fundo escuro */
    .stApp { background-color: #0F172A; color: #FFFFFF; }
    
    /* Forçar todos os textos de Markdown, labels e títulos para Branco */
    h1, h2, h3, p, span, label { color: #FFFFFF !important; }
    
    /* Remover espaços inúteis no topo */
    .block-container { padding-top: 1.5rem !important; padding-bottom: 0rem !important; }
    
    /* Estilo dos Cards de Métricas */
    div[data-testid="stMetric"] {
        background-color: #1E293B;
        padding: 5px 15px;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    div[data-testid="stMetricLabel"] { color: #94A3B8 !important; font-size: 0.85rem !important; }
    div[data-testid="stMetricValue"] { color: #5BC0EB !important; font-size: 1.5rem !important; }

    /* Estilização da Tabela (Fundo escuro e texto claro) */
    .stDataFrame div { color: #FFFFFF !important; }

    /* Ocultar elementos desnecessários */
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# 2. Dados (Otimizados para o exemplo)
def load_data():
    columns = ['Cliente', 'Indicador', 'Categoria', 'Valor', 'Entrada', 'Idade', 'Segundo_Pagto']
    data = [
        ['Ana Silva', 'Instagram', 'ID-DEFINITIVO', 5000, 2500, '20-25', 1000],
        ['Bruno Costa', 'Kalil', 'TRC PROVISÓRIO', 1500, 500, '30-35', 0],
        ['Carla Souza', 'Google', 'AE TODAS', 4500, 4500, '40-45', 0],
        ['Diego Lima', 'Kalil', 'AB CARRO', 8000, 4000, '30-35', 2000],
        ['Erik Rocha', 'Instagram', 'Carta AE', 6000, 3000, '25-30', 1000],
        ['Fernanda Luz', 'Google', 'Renov. CNH', 1200, 1200, '50-55', 0],
    ]
    return pd.DataFrame(data, columns=columns)

df = load_data()
df['Total Pago'] = df['Entrada'] + df['Segundo_Pagto']
df['Saldo'] = df['Valor'] - df['Total Pago']

# 3. Cabeçalho e Métricas (Linha Única)
st.subheader("📊 Executive CRM Dashboard")
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Faturamento", f"R$ {df['Valor'].sum():,.0f}")
m2.metric("Recebido", f"R$ {df['Total Pago'].sum():,.0f}")
m3.metric("Saldo", f"R$ {df['Saldo'].sum():,.0f}")
m4.metric("Vendas", len(df))
m5.metric("Ticket Médio", f"R$ {df['Valor'].mean():,.0f}")
m6.metric("LTV", "R$ 4.2k")

# 4. Grid de Gráficos (Altura reduzida para 180px)
cores = ["#A05195", "#F9B24D", "#2F5D8C", "#5BC0EB", "#665191"]
chart_height = 180

c1, c2, c3 = st.columns([1.2, 1, 1]) # Proporções diferentes para variar o visual

with c1:
    # Gráfico de Barras Horizontal (Canais)
    fig_origem = px.bar(df.groupby("Indicador")["Valor"].sum().reset_index(), 
                        x="Valor", y="Indicador", orientation='h', 
                        title="Vendas por Canal", color_discrete_sequence=[cores[3]])
    fig_origem.update_layout(height=chart_height, margin=dict(l=10, r=10, t=30, b=10), 
                             paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                             font=dict(color="white", size=10), title_font_size=12)
    st.plotly_chart(fig_origem, use_container_width=True)

with c2:
    # Gráfico de Rosca (Categorias)
    fig_cat = px.pie(df, values='Valor', names='Categoria', hole=.5, title="Mix de Produtos")
    fig_cat.update_traces(marker=dict(colors=cores))
    fig_cat.update_layout(height=chart_height, margin=dict(l=10, r=10, t=30, b=10), 
                          paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white", size=10), 
                          showlegend=False, title_font_size=12)
    st.plotly_chart(fig_cat, use_container_width=True)

with c3:
    # Gráfico de Barras (Idade)
    fig_idade = px.bar(df.groupby("Idade")["Valor"].sum().reset_index(), 
                       x="Idade", y="Valor", title="Faturamento por Idade")
    fig_idade.update_traces(marker_color=cores[0])
    fig_idade.update_layout(height=chart_height, margin=dict(l=10, r=10, t=30, b=10), 
                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                            font=dict(color="white", size=10), title_font_size=12)
    st.plotly_chart(fig_idade, use_container_width=True)

# 5. Tabela de Dados (Altura fixa para evitar scroll da página)
st.markdown("### 📋 Detalhamento de Operações")
st.dataframe(
    df[['Cliente', 'Categoria', 'Valor', 'Saldo', 'Indicador']].style.set_properties(**{
        'background-color': '#1E293B',
        'color': 'white',
        'border-color': '#334155'
    }), 
    use_container_width=True, 
    height=160 # Altura pequena para caber na tela
)

# Instrução lateral
st.sidebar.info("Pressione **Ctrl + P** e escolha 'Paisagem' para salvar o PDF em uma única folha A4.")