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

# 2. Sidebar - Importação e Configurações de Leads
st.sidebar.header("📁 Gestão de Dados")
uploaded_file = st.sidebar.file_uploader("Carregue seu arquivo CSV", type=["csv"])

st.sidebar.markdown("---")
st.sidebar.header("🎯 Funil de Vendas")
# Input para cálculo da Taxa de Conversão
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
        # Dados padrão (Exemplo)
        data = [
            ['Ana Silva', 'Instagram', 'VIP', 5000, 2500, '20-25 anos', 1000, '2026-04-10', 'Brasil', 'Não', 'Ok', 'Ok', 'Ok', '5511999999999'],
            ['Bruno Costa', 'Kalil', 'Standard', 1500, 500, '30-35 anos', 0, '2026-04-10', 'Portugal', 'Sim', 'Ok', '', 'Ok', '351910000000'],
            ['Carla Souza', 'Google', 'Premium', 4500, 4500, '40-45 anos', 0, '2026-04-11', 'Brasil', 'Não', '', '', '', '5521988888888'],
            ['Diego Lima', 'Kalil', 'VIP', 8000, 4000, '30-35 anos', 2000, '2026-04-11', 'Angola', 'Sim', 'Ok', 'Ok', '', '244910000000'],
        ]
        return pd.DataFrame(data, columns=columns)

df = load_data()

# 3. Tratamento de Dados
numeric_cols = ['Valor', 'Entrada', 'Segundo_Pagto']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

df['Saldo'] = df['Valor'] - (df['Entrada'] + df['Segundo_Pagto'])

# Limpeza de strings para colunas de status
status_cols = ['Doc enviado', 'Doc Recebido', 'Comissão Larissa']
for col in status_cols:
    df[col] = df[col].fillna('').astype(str).replace({'nan': ''})

total_vendas_count = len(df)
taxa_conversao = (total_vendas_count / total_leads) * 100

# 4. Interface Principal
st.title("📊 CRM Dashboard | Gestão Kalil")
if not uploaded_file:
    st.info("💡 Exibindo dados de exemplo. Carregue seu CSV para atualizar os gráficos.")

st.markdown("---")

# 5. Métricas Principais
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Volume de Vendas", f"R$ {df['Valor'].sum():,.2f}")
m2.metric("Saldo a Receber", f"R$ {df['Saldo'].sum():,.2f}")
m3.metric("Ticket Médio", f"R$ {df['Valor'].mean():,.2f}")
m4.metric("Vendas Fechadas", total_vendas_count)
m5.metric("Conversão", f"{taxa_conversao:.1f}%")

st.markdown("---")

# 6. Relatório de Insights (IA Simulação)
st.markdown("### 🤖 Insights de Performance")
if st.button("Gerar Relatório Analítico"):
    faturamento = df['Valor'].sum()
    leads_necessarios = int(total_leads * 1.5)
    
    st.success(f"""
    * **Análise de Conversão:** Sua taxa atual é de **{taxa_conversao:.1f}%**. Para dobrar o faturamento, mantendo essa taxa, você precisaria de aproximadamente **{leads_necessarios} leads**.
    * **Pendências Financeiras:** O valor de **R$ {df['Saldo'].sum():,.2f}** em aberto representa um risco de inadimplência. Foco no recebimento do 'Segundo Pagamento'.
    * **Documentação:** Apenas {len(df[df['Doc Recebido'] == 'Ok'])} de {len(df)} clientes estão com o processo 100% concluído.
    """)

# 7. GRID DE GRÁFICOS (4 Gráficos Relevantes)
st.markdown("### 📈 Visualizações Gerenciais")

fila1_col1, fila1_col2 = st.columns(2)
fila2_col1, fila2_col2 = st.columns(2)

# --- GRÁFICO 1: Funil de Vendas ---
with fila1_col1:
    df_funil = pd.DataFrame({
        "Etapa": ["Leads", "Vendas"],
        "Qtd": [total_leads, total_vendas_count]
    })
    fig_funil = px.funnel(df_funil, x='Qtd', y='Etapa', title="Funil: Leads vs Fechamento", 
                          color_discrete_sequence=["#2c3e50"])
    st.plotly_chart(fig_funil, use_container_width=True)

# --- GRÁFICO 2: Faturamento por Indicador (Origem) ---
with fila1_col2:
    fig_origem = px.bar(
        df.groupby("Indicador")["Valor"].sum().reset_index().sort_values("Valor"),
        x="Valor", y="Indicador", orientation='h',
        title="Faturamento por Canal de Origem",
        text_auto='.2s', color_discrete_sequence=["#bb463c"]
    )
    st.plotly_chart(fig_origem, use_container_width=True)

# --- GRÁFICO 3: Ticket Médio por Categoria ---
with fila2_col1:
    fig_ticket = px.bar(
        df.groupby("Categoria")["Valor"].mean().reset_index(),
        x="Categoria", y="Valor",
        title="Ticket Médio por Categoria",
        color="Categoria", color_discrete_sequence=px.colors.qualitative.Safe
    )
    st.plotly_chart(fig_ticket, use_container_width=True)

# --- GRÁFICO 4: Distribuição por País ---
with fila2_col2:
    fig_pais = px.pie(
        df, names='País', values='Valor',
        title="Participação de Vendas por País",
        hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(fig_pais, use_container_width=True)

# 8. Tabela com Status (Correção do applymap para map)
st.markdown("### 📋 Detalhamento dos Clientes e Status")

def color_ok(val):
    return 'background-color: #d4edda' if val == 'Ok' else ''

st.dataframe(
    df.style.map(color_ok, subset=['Doc enviado', 'Doc Recebido', 'Comissão Larissa'])
            .format({'Valor': 'R$ {:.2f}', 'Saldo': 'R$ {:.2f}', 'Entrada': 'R$ {:.2f}', 'Segundo_Pagto': 'R$ {:.2f}'}),
    use_container_width=True
)