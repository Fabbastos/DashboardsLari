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
total_leads = st.sidebar.number_input("Total de Leads (Contatos)", min_value=1, value=40)

# Função para carregar os dados
def load_data():
    # Colunas atualizadas conforme pedido
    columns = [
        'Cliente', 'Indicador', 'Categoria', 'Valor', 'Entrada', 
        'Idade', 'Segundo_Pagto', 'Data', 'País', 'Indicação_Kalil',
        'Doc enviado', 'Doc Recebido', 'Comissão Larissa', 'telefone'
    ]
    
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    else:
        # Dados padrão atualizados com as novas colunas
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

# Preenche vazios nas colunas de status para evitar erros visualização
status_cols = ['Doc enviado', 'Doc Recebido', 'Comissão Larissa']
for col in status_cols:
    df[col] = df[col].fillna('').replace({'nan': ''})

total_vendas_count = len(df)
taxa_conversao = (total_vendas_count / total_leads) * 100

# 4. Interface Principal
st.title("📊 CRM Dashboard | Gestão Kalil")
if not uploaded_file:
    st.info("💡 Usando dados demonstrativos. Use a barra lateral para carregar seu CSV.")

st.markdown("---")

# 5. Métricas Principais
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Volume de Vendas", f"R$ {df['Valor'].sum():,.2f}")
m2.metric("Saldo a Receber", f"R$ {df['Saldo'].sum():,.2f}")
m3.metric("Ticket Médio", f"R$ {df['Valor'].mean():,.2f}")
m4.metric("Taxa de Conversão", f"{taxa_conversao:.1f}%")
# Nova métrica de pendência documental
docs_pendentes = len(df[df['Doc Recebido'] != 'Ok'])
m5.metric("Docs Pendentes", docs_pendentes, delta=f"{docs_pendentes} clientes", delta_color="inverse")

st.markdown("---")

# 6. Relatório Inteligente (Simulação de IA)
st.markdown("### 🤖 Insights de Performance")
if st.button("Gerar Análise Crítica"):
    comissao_paga = len(df[df['Comissão Larissa'] == 'Ok'])
    relatorio = f"""
    - **Conversão:** Sua taxa de **{taxa_conversao:.1f}%** está dentro do esperado para o tráfego atual.
    - **Documentação:** Existem **{docs_pendentes}** processos com documentação incompleta. Isso pode atrasar o recebimento do saldo de R$ {df['Saldo'].sum():,.2f}.
    - **Comissões:** Das {len(df)} vendas, **{comissao_paga}** comissões da Larissa já foram processadas.
    - **Atenção:** Verifique os telefones dos clientes de **{df.groupby('País')['Valor'].sum().idxmax()}**, que é o seu maior mercado hoje.
    """
    st.success(relatorio)

# 7. Seção de Gráficos
st.markdown("### 📈 Análise Visual")

c1, c2 = st.columns(2)
with c1:
    dados_funil = pd.DataFrame({
        "Etapa": ["Leads (Contatos)", "Vendas Fechadas"],
        "Quantidade": [total_leads, total_vendas_count]
    })
    fig_funil = px.funnel(dados_funil, x='Quantidade', y='Etapa', title="Funil de Vendas", color_discrete_sequence=["#2c3e50"])
    st.plotly_chart(fig_funil, use_container_width=True)

with c2:
    fig_origem_val = px.bar(
        df.groupby("Indicador")["Valor"].sum().reset_index(),
        x="Indicador", y="Valor",
        title="Faturamento por Canal",
        text_auto='.2s',
        color_discrete_sequence=["#bb463c"]
    )
    st.plotly_chart(fig_origem_val, use_container_width=True)

# 8. Tabela de Dados com Formatação Condicional
st.markdown("### 📋 Detalhamento e Status de Processos")

# Função para colorir as células de OK
def color_ok(val):
    color = '#d4edda' if val == 'Ok' else ''
    return f'background-color: {color}'

# Exibe a tabela formatada
st.dataframe(
    df.style.applymap(color_ok, subset=status_cols)
            .format({'Valor': 'R$ {:.2f}', 'Saldo': 'R$ {:.2f}'}),
    use_container_width=True
)