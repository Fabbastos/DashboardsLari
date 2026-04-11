import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="CRM Vendas Premium", layout="wide", page_icon="📊")

# Estilização para o tom "Premium"
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar - Gestão de Dados
st.sidebar.header("📁 Gestão de Dados")
uploaded_file = st.sidebar.file_uploader("Carregue seu arquivo CSV", type=["csv"])

st.sidebar.markdown("---")
st.sidebar.header("🎯 Funil de Vendas")
total_leads = st.sidebar.number_input("Total de Leads (Contatos)", min_value=1, value=40)

# Função para carregar os dados
def load_data():
    columns = [
        'Cliente', 'Indicador', 'Categoria', 'Valor', 'Entrada', 
        'Idade', 'Segundo_Pagto', 'Data', 'País', 'Indicação_Kalil',
        'Doc enviado', 'Doc Recebido', 'Comissão Larissa', 'telefone'
    ]
    
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    else:
        # Dados padrão com as SUAS CATEGORIAS REAIS
        data = [
            ['Ana Silva', 'Instagram', 'ID-DEFINITIVO', 5000, 2500, '20-25 anos', 1000, '2026-04-10', 'Brasil', 'Não', 'Ok', 'Ok', 'Ok', '5511999999999'],
            ['Bruno Costa', 'Kalil', 'TRC PROVISÓRIO', 1500, 500, '30-35 anos', 0, '2026-04-10', 'Portugal', 'Sim', 'Ok', '', 'Ok', '351910000000'],
            ['Carla Souza', 'Google', 'AE TODAS AS CATEGORIAS', 4500, 4500, '40-45 anos', 0, '2026-04-11', 'Brasil', 'Não', '', '', '', '5521988888888'],
            ['Diego Lima', 'Kalil', 'AB CARRO E MOTO', 8000, 4000, '30-35 anos', 2000, '2026-04-11', 'Angola', 'Sim', 'Ok', 'Ok', '', '244910000000'],
            ['Erik Rocha', 'Instagram', 'Carta AE polonia', 6000, 3000, '25-30 anos', 1000, '2026-04-12', 'Brasil', 'Não', 'Ok', 'Ok', 'Ok', '5511977777777'],
            ['Fernanda Luz', 'Google', 'Renov. CNH', 1200, 1200, '50-55 anos', 0, '2026-04-12', 'Portugal', 'Não', 'Ok', 'Ok', '', '351920000000'],
        ]
        return pd.DataFrame(data, columns=columns)

df = load_data()

# 3. Tratamento de Dados
numeric_cols = ['Valor', 'Entrada', 'Segundo_Pagto']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

df['Saldo'] = df['Valor'] - (df['Entrada'] + df['Segundo_Pagto'])

status_cols = ['Doc enviado', 'Doc Recebido', 'Comissão Larissa']
for col in status_cols:
    df[col] = df[col].fillna('').astype(str).replace({'nan': ''})

total_vendas_count = len(df)
taxa_conversao = (total_vendas_count / total_leads) * 100

# 4. Interface Principal
st.title("📊 CRM Dashboard | Gestão Kalil")
st.markdown("---")

# 5. Métricas em Duas Linhas (Para evitar o corte do texto/número)
st.markdown("### 📊 Resumo Executivo")
m_row1_1, m_row1_2, m_row1_3 = st.columns(3)
m_row2_1, m_row2_2 = st.columns(2)

with m_row1_1:
    st.metric("Volume de Vendas", f"R$ {df['Valor'].sum():,.2f}")
with m_row1_2:
    st.metric("Saldo a Receber", f"R$ {df['Saldo'].sum():,.2f}")
with m_row1_3:
    st.metric("Ticket Médio", f"R$ {df['Valor'].mean():,.2f}")

with m_row2_1:
    st.metric("Vendas Fechadas", f"{total_vendas_count} unid.")
with m_row2_2:
    st.metric("Taxa de Conversão", f"{taxa_conversao:.1f}%")

st.markdown("---")

# 6. Relatório de Insights
st.markdown("### 🤖 Insights de Performance")
if st.button("Gerar Relatório Analítico"):
    faturamento = df['Valor'].sum()
    top_cat = df.groupby('Categoria')['Valor'].sum().idxmax()
    st.success(f"**Insight:** A categoria com maior faturamento é **{top_cat}**. Sua conversão de **{taxa_conversao:.1f}%** indica que para cada 10 leads, você fecha aproximadamente {int(taxa_conversao/10)} venda(s).")

# 7. Grid de Gráficos 2x2
st.markdown("### 📈 Visualizações Gerenciais")
c1, c2 = st.columns(2)
c3, c4 = st.columns(2)

with c1:
    # Funil
    fig_funil = px.funnel(pd.DataFrame({"Etapa": ["Leads", "Vendas"], "Qtd": [total_leads, total_vendas_count]}), 
                          x='Qtd', y='Etapa', title="Funil de Vendas", color_discrete_sequence=["#2c3e50"])
    st.plotly_chart(fig_funil, use_container_width=True)

with c2:
    # Faturamento por Indicador
    fig_origem = px.bar(df.groupby("Indicador")["Valor"].sum().reset_index().sort_values("Valor"),
                        x="Valor", y="Indicador", orientation='h', title="Faturamento por Canal",
                        text_auto='.2s', color_discrete_sequence=["#bb463c"])
    st.plotly_chart(fig_origem, use_container_width=True)

with c3:
    # Faturamento por Categoria (As suas categorias reais)
    fig_cat = px.bar(df.groupby("Categoria")["Valor"].sum().reset_index().sort_values("Valor"),
                     x="Categoria", y="Valor", title="Faturamento por Categoria",
                     color="Categoria", color_discrete_sequence=px.colors.qualitative.Prism)
    st.plotly_chart(fig_cat, use_container_width=True)

with c4:
    # Participação por País
    fig_pais = px.pie(df, names='País', values='Valor', title="Vendas por País", hole=0.4)
    st.plotly_chart(fig_pais, use_container_width=True)

# 8. Tabela com Status (Corrigida)
st.markdown("### 📋 Detalhamento e Status")

def color_ok(val):
    return 'background-color: #d4edda' if val == 'Ok' else ''

st.dataframe(
    df.style.map(color_ok, subset=['Doc enviado', 'Doc Recebido', 'Comissão Larissa'])
            .format({'Valor': 'R$ {:.2f}', 'Saldo': 'R$ {:.2f}', 'Entrada': 'R$ {:.2f}', 'Segundo_Pagto': 'R$ {:.2f}'}),
    use_container_width=True
)