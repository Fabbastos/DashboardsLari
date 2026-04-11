import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="CRM Vendas Premium", layout="wide", page_icon="📊")

# --- Estilização Corrigida (Contraste e Fontes) ---
st.markdown("""
    <style>
    /* Força o texto para uma cor legível (evita o bug do dark mode do Streamlit) */
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    
    .stMetric label { font-size: 1.2rem !important; font-weight: bold !important; color: #2c3e50 !important; }
    .stMetric div[data-testid="stMetricValue"] { font-size: 2.0rem !important; font-weight: bold !important; color: #bb463c !important; }
    
    /* Relatório IA - Fundo claro com texto escuro OBRIGATÓRIO */
    .ia-report { 
        background-color: #e3f2fd !important; 
        color: #1e1e1e !important; /* Garante que o texto será escuro */
        border-left: 5px solid #2196f3; 
        padding: 20px; 
        border-radius: 8px; 
        font-size: 1.15rem; 
    }
    .ia-report h3 { color: #0d47a1 !important; margin-top: 0; }
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
        # Dados padrão
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
df['Total Pago'] = df['Entrada'] + df['Segundo_Pagto']

status_cols = ['Doc enviado', 'Doc Recebido', 'Comissão Larissa']
for col in status_cols:
    df[col] = df[col].fillna('').astype(str).replace({'nan': ''})

total_vendas_count = len(df)
total_pago = df['Total Pago'].sum()
taxa_conversao = (total_vendas_count / total_leads) * 100

# 4. Interface Principal
st.title("📊 CRM Dashboard | Gestão Kalil")
st.markdown("---")

# 5. Métricas em Duas Linhas
st.markdown("### 📈 Resumo Analítico")
m_row1_1, m_row1_2, m_row1_3 = st.columns(3)
m_row2_1, m_row2_2, m_row2_3 = st.columns(3)

with m_row1_1:
    st.metric("Faturamento Total", f"R$ {df['Valor'].sum():,.2f}")
with m_row1_2:
    st.metric("Total Pago", f"R$ {total_pago:,.2f}")
with m_row1_3:
    st.metric("Saldo a Receber", f"R$ {df['Saldo'].sum():,.2f}")

with m_row2_1:
    st.metric("Ticket Médio", f"R$ {df['Valor'].mean():,.2f}")
with m_row2_2:
    st.metric("Conversão", f"{taxa_conversao:.1f}%")
with m_row2_3:
    top_idade = df.groupby('Idade')['Cliente'].count().idxmax() if not df.empty else "N/A"
    st.metric("Público Alvo", top_idade)

st.markdown("---")

# 6. Relatório de Insights (Cores Legíveis)
st.markdown("### 🤖 Gerador de Insights Estratégicos")
if st.button("Gerar Relatório Completo"):
    top_cat = df.groupby('Categoria')['Valor'].sum().idxmax() if not df.empty else "N/A"
    top_indicador = df.groupby('Indicador')['Valor'].sum().idxmax() if not df.empty else "N/A"
    faturamento = df['Valor'].sum()
    leads_necessarios = int(total_leads * 1.5)
    saldo_receber = df['Saldo'].sum()
    
    report_text = f"""
    ### Análise Executiva:
    O faturamento total alcançou **R$ {faturamento:,.2f}**, impulsionado pela categoria **{top_cat}**. O canal **{top_indicador}** foi o mais lucrativo, exigindo atenção especial.

    ### Performance do Funil:
    Sua conversão está em **{taxa_conversao:.1f}%**. Para dobrar seu faturamento atual, mantendo essa eficiência, você precisará captar aproximadamente **{leads_necessarios} leads**.

    ### Saúde Financeira:
    O saldo a receber é de **R$ {saldo_receber:,.2f}**. Isso representa um risco de inadimplência caso não haja cobrança ativa para os pagamentos da segunda parcela.
    """
    st.markdown(f'<div class="ia-report">{report_text}</div>', unsafe_allow_html=True)

st.markdown("---")

# 7. Grid de Gráficos 2x2 (Tamanhos Reduzidos para Caber na Tela)
st.markdown("### 📈 Visualizações Gerenciais")
c1, c2 = st.columns(2)
c3, c4 = st.columns(2)

altura_graficos = 320 # Reduzindo a altura para ficar mais compacto

with c1:
    df_funil = pd.DataFrame({"Etapa": ["Leads", "Vendas"], "Qtd": [total_leads, total_vendas_count]})
    fig_funil = px.funnel(df_funil, x='Qtd', y='Etapa', title="Funil de Conversão")
    fig_funil.update_traces(marker=dict(color=["#e74c3c", "#27ae60"]))
    fig_funil.update_layout(height=altura_graficos, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_funil, use_container_width=True)

with c2:
    fig_origem = px.bar(df.groupby("Indicador")["Valor"].sum().reset_index().sort_values("Valor"),
                        x="Valor", y="Indicador", orientation='h', title="Faturamento por Canal",
                        text_auto='.2s', color="Indicador",
                        color_discrete_sequence=px.colors.qualitative.Antique)
    fig_origem.update_layout(height=altura_graficos, margin=dict(l=10, r=10, t=40, b=10), showlegend=False)
    st.plotly_chart(fig_origem, use_container_width=True)

with c3:
    fig_cat = px.bar(df.groupby("Categoria")["Valor"].sum().reset_index().sort_values("Valor"),
                     x="Categoria", y="Valor", title="Faturamento por Categoria",
                     color="Categoria", color_discrete_sequence=px.colors.qualitative.Bold)
    fig_cat.update_layout(height=altura_graficos, margin=dict(l=10, r=10, t=40, b=10), showlegend=False)
    st.plotly_chart(fig_cat, use_container_width=True)

with c4:
    fig_idade = px.bar(df.groupby("Idade")["Valor"].sum().reset_index().sort_values("Valor"),
                       x="Idade", y="Valor", title="Faturamento por Faixa Etária",
                       color="Idade", color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_idade.update_layout(height=altura_graficos, margin=dict(l=10, r=10, t=40, b=10), showlegend=False)
    st.plotly_chart(fig_idade, use_container_width=True)

# 8. Tabela com Status
st.markdown("### 📋 Detalhamento e Status")

def color_ok(val):
    return 'background-color: #d4edda; color: #155724;' if val == 'Ok' else '' # Verde mais forte para leitura

st.dataframe(
    df.style.map(color_ok, subset=['Doc enviado', 'Doc Recebido', 'Comissão Larissa'])
            .format({'Valor': 'R$ {:.2f}', 'Saldo': 'R$ {:.2f}', 'Entrada': 'R$ {:.2f}', 'Segundo_Pagto': 'R$ {:.2f}', 'Total Pago': 'R$ {:.2f}'}),
    use_container_width=True
)