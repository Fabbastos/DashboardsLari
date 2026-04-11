import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Executive CRM", layout="wide", page_icon="📊")

# --- CSS: Otimização de Espaço e Cores ---
st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #FFFFFF; }
    
    /* ZERAR espaço do topo e margens */
    .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; padding-left: 2rem; padding-right: 2rem; }
    #MainMenu, footer, header { display: none !important; }
    
    /* Forçar títulos e textos para branco brilhante */
    h1, h2, h3, p, span, label, .stMarkdown { color: #FFFFFF !important; }
    
    /* Cards de Métricas */
    div[data-testid="stMetric"] {
        background-color: #1E293B;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    div[data-testid="stMetricLabel"] { color: #CBD5E1 !important; font-size: 0.9rem !important; }
    div[data-testid="stMetricValue"] { color: #5BC0EB !important; font-size: 1.5rem !important; font-weight: bold; }

    </style>
    """, unsafe_allow_html=True)

# 2. Dados de Exemplo
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

# Cálculo da Diferença
fat_lead = df[df['Canal'] == 'Lead']['Valor'].sum()
fat_kalil = df[df['Canal'] == 'Kalil']['Valor'].sum()
diff_fat = abs(fat_lead - fat_kalil)
vencedor = "Lead" if fat_lead > fat_kalil else "Kalil"

# 3. Cabeçalho
st.markdown("<h2 style='margin-top: 5px; margin-bottom: 10px; font-weight: bold;'>📊 Executive CRM Dashboard</h2>", unsafe_allow_html=True)

# Linha de Métricas
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Faturamento", f"R$ {df['Valor'].sum():,.0f}")
m2.metric("Recebido", f"R$ {df['Total Pago'].sum():,.0f}")
m3.metric("Saldo", f"R$ {df['Saldo'].sum():,.0f}")
m4.metric("Vendas Fechadas", len(df))
m5.metric("Ticket Médio", f"R$ {df['Valor'].mean():,.0f}")
m6.metric(f"Vantagem ({vencedor})", f"+ R$ {diff_fat:,.0f}")

# --- Configuração de Estilo dos Gráficos (FONTES MAIORES E MAIS CLARAS) ---
cores = ["#5BC0EB", "#F9B24D", "#A05195", "#2F5D8C", "#665191"]
chart_height = 240 

def aplicar_estilo_dark(fig, is_bar=False):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        # Aumentado o tamanho geral das fontes e forçado branco puro
        font=dict(color="#FFFFFF", size=13), 
        # Títulos bem maiores
        title_font=dict(color="#FFFFFF", size=16, family="Arial Black"),
        margin=dict(l=10, r=10, t=40, b=10),
        height=chart_height,
        # Legenda maior e branca
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=12, color="#FFFFFF"))
    )
    
    # Eixos X e Y com letras mais claras e maiores
    fig.update_xaxes(gridcolor='#1E293B', zerolinecolor='#1E293B', tickfont=dict(color="#FFFFFF", size=12))
    fig.update_yaxes(gridcolor='#1E293B', zerolinecolor='#1E293B', tickfont=dict(color="#FFFFFF", size=12))
    
    if is_bar:
        fig.update_layout(bargap=0.4) 
        
    return fig

st.write("") 

# 4. Primeira Fileira de Gráficos (3 colunas)
c1, c2, c3 = st.columns(3)

with c1:
    # 1. FUNIL COMPARATIVO
    vendas_lead = len(df[df['Canal'] == 'Lead'])
    vendas_kalil = len(df[df['Canal'] == 'Kalil'])
    df_funil = pd.DataFrame({
        'Etapa': ['1. Contatos', '2. Vendas', '1. Contatos', '2. Vendas'],
        'Origem': ['Lead', 'Lead', 'Kalil', 'Kalil'],
        'Qtd': [40, vendas_lead, 12, vendas_kalil] 
    })
    fig1 = px.funnel(df_funil, x='Qtd', y='Etapa', color='Origem', 
                     title="Conversão por Canal", color_discrete_sequence=[cores[0], cores[1]])
    
    # Forçar os números dentro do funil a ficarem grandes e brancos
    fig1.update_traces(textfont=dict(color="#FFFFFF", size=14, family="Arial Black"))
    st.plotly_chart(aplicar_estilo_dark(fig1), use_container_width=True)

with c2:
    # 2. MIX DE PRODUTOS (Substituiu o Treemap por Barras Horizontais)
    df_cat = df.groupby("Categoria")["Valor"].sum().reset_index().sort_values("Valor")
    fig2 = px.bar(df_cat, x="Valor", y="Categoria", orientation='h', 
                  title="Mix de Produtos", color_discrete_sequence=[cores[2]])
    st.plotly_chart(aplicar_estilo_dark(fig2, is_bar=True), use_container_width=True)

with c3:
    # 3. FATURAMENTO POR IDADE E CANAL 
    fig3 = px.bar(df.groupby(["Idade", "Canal"])["Valor"].sum().reset_index(), 
                  x="Idade", y="Valor", color="Canal", title="Faturamento por Idade",
                  color_discrete_sequence=[cores[0], cores[1]], barmode='group')
    st.plotly_chart(aplicar_estilo_dark(fig3, is_bar=True), use_container_width=True)


# 5. Segunda Fileira de Gráficos (3 colunas)
c4, c5, c6 = st.columns(3)

with c4:
    # 4. VENDAS POR PAÍS
    fig4 = px.bar(df.groupby(["País", "Canal"])["Valor"].sum().reset_index(), 
                  x="País", y="Valor", color="Canal", title="Faturamento por País",
                  color_discrete_sequence=[cores[0], cores[1]])
    st.plotly_chart(aplicar_estilo_dark(fig4, is_bar=True), use_container_width=True)

with c5:
    # 5. STATUS DE DOCUMENTAÇÃO 
    fig5 = px.bar(df.groupby(["Doc_Status", "Canal"])["Valor"].count().reset_index(), 
                  x="Valor", y="Doc_Status", color="Canal", orientation='h', 
                  title="Documentos (Qtd Clientes)", color_discrete_sequence=[cores[0], cores[1]])
    st.plotly_chart(aplicar_estilo_dark(fig5, is_bar=True), use_container_width=True)

with c6:
    # 6. SALDO A RECEBER 
    df_devedor = df[df['Saldo'] > 0]
    fig6 = px.bar(df_devedor, x="Cliente", y="Saldo", color="Canal", 
                  title="Saldo Devedor por Cliente", color_discrete_sequence=[cores[0], cores[1]])
    st.plotly_chart(aplicar_estilo_dark(fig6, is_bar=True), use_container_width=True)