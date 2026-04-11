import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="CRM Vendas Premium", layout="wide", page_icon="📊")

# Estilização básica para manter o tom "Premium"
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar - Importação de Dados
st.sidebar.header("📁 Importação de Dados")
uploaded_file = st.sidebar.file_uploader("Carregue seu arquivo CSV do CRM", type=["csv"])

# Função para carregar os dados
def load_data():
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    else:
        # Dados padrão
        data = [
            ['Ana Silva', 'Instagram', 'VIP', 5000, 2500, '20-25 anos', 1000, '2026-04-10', 'Brasil', 'Não'],
            ['Bruno Costa', 'Kalil', 'Standard', 1500, 500, '30-35 anos', 0, '2026-04-10', 'Portugal', 'Sim'],
            ['Carla Souza', 'Google', 'Premium', 4500, 4500, '40-45 anos', 0, '2026-04-11', 'Brasil', 'Não'],
            ['Diego Lima', 'Kalil', 'VIP', 8000, 4000, '30-35 anos', 2000, '2026-04-11', 'Angola', 'Sim'],
        ]
        columns = ['Cliente', 'Indicador', 'Categoria', 'Valor', 'Entrada', 'Idade', 'Segundo_Pagto', 'Data', 'País', 'Indicação_Kalil']
        return pd.DataFrame(data, columns=columns)

df = load_data()

# 3. Tratamento de Dados
numeric_cols = ['Valor', 'Entrada', 'Segundo_Pagto']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

df['Saldo'] = df['Valor'] - (df['Entrada'] + df['Segundo_Pagto'])

# 4. Interface Principal e Cabeçalho
st.title("📊 CRM Dashboard | Gestão Kalil")
if uploaded_file:
    st.success(f"Arquivo '{uploaded_file.name}' carregado com sucesso!")
else:
    st.info("Exibindo dados de demonstração. Carregue um CSV na barra lateral para atualizar.")

st.markdown("---")

# 5. Relatório Inteligente (Simulação de IA)
st.markdown("### 🤖 Gerador de Insights Analíticos")
if st.button("Gerar Relatório dos Dados Atuais"):
    # Cálculos dinâmicos para a "IA"
    total_vendas = df['Valor'].sum()
    top_pais = df.groupby('País')['Valor'].sum().idxmax()
    top_origem = df.groupby('Indicador')['Valor'].sum().idxmax()
    perc_receber = (df['Saldo'].sum() / total_vendas) * 100 if total_vendas > 0 else 0
    qtd_vip = len(df[df['Categoria'] == 'VIP'])
    
    # Texto gerado dinamicamente
    relatorio = f"""
    **Análise Executiva:**
    Identificamos que o faturamento total alcançou **R$ {total_vendas:,.2f}**, sendo o mercado de **{top_pais}** o principal responsável pelo volume financeiro atual.
    
    A principal fonte de atração de clientes pagantes neste período foi via **{top_origem}**. Atualmente, você possui **{qtd_vip} cliente(s) VIP** na sua base ativa.
    
    **Ponto de Atenção:** Aproximadamente **{perc_receber:.1f}%** do valor das vendas ainda está pendente (Saldo a Receber). Recomenda-se acionar a equipe de cobrança para os pagamentos de segunda parcela.
    """
    st.info(relatorio)

st.markdown("---")

# 6. Métricas Principais
m1, m2, m3, m4 = st.columns(4)
m1.metric("Volume de Vendas", f"R$ {df['Valor'].sum():,.2f}")
m2.metric("Saldo a Receber", f"R$ {df['Saldo'].sum():,.2f}")
m3.metric("Ticket Médio", f"R$ {df['Valor'].mean():,.2f}")
m4.metric("Total Clientes", len(df))

# 7. Seção de Gráficos 2D
st.markdown("### 📈 Visualizações Essenciais")
col1, col2 = st.columns(2)

with col1:
    fig_pais = px.bar(
        df.groupby("País")["Valor"].sum().sort_values(ascending=True).reset_index(),
        x="Valor", y="País", orientation="h",
        title="Faturamento por País",
        color_discrete_sequence=["#bb463c"],
        text_auto='.2s'
    )
    st.plotly_chart(fig_pais, use_container_width=True)

with col2:
    fig_cat = px.pie(
        df, names='Categoria', values='Valor',
        title="Mix de Categorias (Valor)",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    st.plotly_chart(fig_cat, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    fig_origem = px.bar(
        df.groupby("Indicador")["Cliente"].count().reset_index(),
        x="Indicador", y="Cliente",
        title="Quantidade de Clientes por Origem",
        labels={'Cliente': 'Qtd Clientes'},
        color_discrete_sequence=["#2c3e50"]
    )
    st.plotly_chart(fig_origem, use_container_width=True)

with col4:
    df_pag = pd.DataFrame({
        'Status': ['Recebido', 'A Receber'],
        'Total': [(df['Entrada'] + df['Segundo_Pagto']).sum(), df['Saldo'].sum()]
    })
    fig_pag = px.pie(df_pag, values='Total', names='Status', title="Saúde Financeira (Fluxo)",
                     color_discrete_sequence=["#27ae60", "#e74c3c"])
    st.plotly_chart(fig_pag, use_container_width=True)

# 8. Gráfico 3D Multidimensional
st.markdown("### 🌌 Mapeamento de Vendas em 3D")
# Relaciona País (Eixo X), Categoria (Eixo Y) e Valor da Venda (Eixo Z - Altura), colorindo pela Origem
fig_3d = px.scatter_3d(
    df, 
    x='País', 
    y='Categoria', 
    z='Valor',
    color='Indicador', 
    size='Valor', 
    hover_name='Cliente',
    title="Análise Cruzada: País x Categoria x Valor",
    color_discrete_sequence=px.colors.qualitative.Prism
)
# Ajusta o tamanho do gráfico 3D
fig_3d.update_layout(margin=dict(l=0, r=0, b=0, t=40), height=600)
st.plotly_chart(fig_3d, use_container_width=True)

# 9. Tabela de Dados
st.markdown("### 📋 Visualização dos Dados Brutos")
st.dataframe(df, use_container_width=True)