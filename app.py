import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="CRM Vendas Premium", layout="wide", page_icon="📊")

# --- Estilização para o tom "Premium" e Fontes Maiores ---
st.markdown("""
    <style>
    /* Cor de fundo e fonte geral */
    .main { background-color: #f5f5f5; font-size: 1.1rem; }
    
    /* Estilo dos Cards (Métricas) */
    .stMetric { background-color: #ffffff; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    
    /* Aumentar Títulos dos Cards */
    .stMetric label { font-size: 1.3rem !important; font-weight: bold !important; color: #2c3e50 !important; }
    
    /* Aumentar Números dos Cards */
    .stMetric div[data-testid="stMetricValue"] { font-size: 2.2rem !important; font-weight: bold !important; color: #bb463c !important; }
    
    /* Aumentar Títulos Gerais (Markdown) */
    h1 { font-size: 2.5rem !important; }
    h2 { font-size: 2.1rem !important; }
    h3 { font-size: 1.7rem !important; }
    
    /* Estilo para a IA Simulação */
    .ia-report { background-color: #e3f2fd; border-left: 5px solid #2196f3; padding: 20px; border-radius: 8px; font-size: 1.15rem; }
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

# Cálculos Chave
df['Saldo'] = df['Valor'] - (df['Entrada'] + df['Segundo_Pagto'])
df['Total Pago'] = df['Entrada'] + df['Segundo_Pagto'] # NOVA COLUNA

status_cols = ['Doc enviado', 'Doc Recebido', 'Comissão Larissa']
for col in status_cols:
    df[col] = df[col].fillna('').astype(str).replace({'nan': ''})

total_vendas_count = len(df)
total_pago = df['Total Pago'].sum() # NOVA MÉTRICA
taxa_conversao = (total_vendas_count / total_leads) * 100

# 4. Interface Principal
st.title("📊 CRM Dashboard | Gestão Kalil")
if not uploaded_file:
    st.info("💡 Exibindo dados de exemplo. Carregue seu CSV para atualizar os gráficos.")

st.markdown("---")

# 5. Métricas em Duas Linhas (Para evitar o corte e com fontes maiores)
st.markdown("### 📈 Resumo Analítico")
m_row1_1, m_row1_2, m_row1_3 = st.columns(3)
m_row2_1, m_row2_2, m_row2_3 = st.columns(3)

with m_row1_1:
    st.metric("Faturamento Total", f"R$ {df['Valor'].sum():,.2f}")
with m_row1_2:
    st.metric("Total Pago", f"R$ {total_pago:,.2f}") # NOVO CARD
with m_row1_3:
    st.metric("Saldo a Receber", f"R$ {df['Saldo'].sum():,.2f}")

with m_row2_1:
    st.metric("Ticket Médio", f"R$ {df['Valor'].mean():,.2f}")
with m_row2_2:
    st.metric("Conversão", f"{taxa_conversao:.1f}%")
with m_row2_3:
    # Faixa etária dominante
    top_idade = df.groupby('Idade')['Cliente'].count().idxmax()
    st.metric("Público Alvo", top_idade) # NOVO CARD

st.markdown("---")

# 6. Relatório de Insights (Expandido e Aumentado)
st.markdown("### 🤖 Gerador de Insights Estratégicos")
if st.button("Gerar Relatório Completo"):
    top_cat = df.groupby('Categoria')['Valor'].sum().idxmax()
    top_indicador = df.groupby('Indicador')['Valor'].sum().idxmax()
    faturamento = df['Valor'].sum()
    leads_necessarios = int(total_leads * 1.5)
    saldo_receber = df['Saldo'].sum()
    
    report_text = f"""
    ### Análise Executiva:
    O faturamento total alcançou **R$ {faturamento:,.2f}**, impulsionado pela categoria **{top_cat}**. O canal de indicador **{top_indicador}** foi o mais lucrativo, exigindo atenção especial.

    ### Performance do Funil:
    Sua conversão está em **{taxa_conversao:.1f}%**. Para dobrar seu faturamento atual, mantendo essa eficiência, você precisará captar aproximadamente **{leads_necessarios} leads**.

    ### Saúde Financeira:
    O saldo a receber é de **R$ {saldo_receber:,.2f}**. Isso representa um risco de inadimplência caso não haja cobrança ativa para os pagamentos de segunda parcela.
    """
    st.markdown(f'<div class="ia-report">{report_text}</div>', unsafe_allow_html=True)

st.markdown("---")

# 7. Grid de Gráficos 2x2 Relevantes
st.markdown("### 📈 Visualizações Gerenciais")
c1, c2 = st.columns(2)
c3, c4 = st.columns(2)

with c1:
    # --- GRÁFICO 1: Funil com Cores Vermelho (Cima) / Verde (Baixo) ---
    df_funil = pd.DataFrame({"Etapa": ["Leads", "Vendas"], "Qtd": [total_leads, total_vendas_count]})
    fig_funil = px.funnel(df_funil, x='Qtd', y='Etapa', title="Funil de Conversão")
    
    # Lógica de cor manual para o funil
    fig_funil.update_traces(marker=dict(color=["#e74c3c", "#27ae60"])) # Vermelho (Leads) e Verde (Vendas)
    st.plotly_chart(fig_funil, use_container_width=True)

with c2:
    # --- GRÁFICO 2: Faturamento por Indicador (COLORIDO) ---
    fig_origem = px.bar(df.groupby("Indicador")["Valor"].sum().reset_index().sort_values("Valor"),
                        x="Valor", y="Indicador", orientation='h', title="Faturamento por Canal",
                        text_auto='.2s', color="Indicador", # COLORIDO PELO CANAL
                        color_discrete_sequence=px.colors.qualitative.Antique)
    st.plotly_chart(fig_origem, use_container_width=True)

with c3:
    # --- GRÁFICO 3: Faturamento por Categoria ---
    fig_cat = px.bar(df.groupby("Categoria")["Valor"].sum().reset_index().sort_values("Valor"),
                     x="Categoria", y="Valor", title="Faturamento por Categoria",
                     color="Categoria", color_discrete_sequence=px.colors.qualitative.Bold)
    st.plotly_chart(fig_cat, use_container_width=True)

with c4:
    # --- GRÁFICO 4: Faturamento por Faixa de Idade (NOVO) ---
    fig_idade = px.bar(df.groupby("Idade")["Valor"].sum().reset_index().sort_values("Valor"),
                       x="Idade", y="Valor", title="Faturamento por Faixa de Idade",
                       color="Idade", color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_idade, use_container_width=True)

# 8. Tabela com Status (Corrigida e Maior)
st.markdown("### 📋 Detalhamento e Status")

def color_ok(val):
    return 'background-color: #d4edda' if val == 'Ok' else ''

st.dataframe(
    df.style.map(color_ok, subset=['Doc enviado', 'Doc Recebido', 'Comissão Larissa'])
            .format({'Valor': 'R$ {:.2f}', 'Saldo': 'R$ {:.2f}', 'Entrada': 'R$ {:.2f}', 'Segundo_Pagto': 'R$ {:.2f}', 'Total Pago': 'R$ {:.2f}'}),
    use_container_width=True
)