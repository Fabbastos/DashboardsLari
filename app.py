import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="CRM Vendas Premium", layout="wide", page_icon="📊")

# --- Estilização Dark Mode Premium (Inspirado no Dashboard de RH) ---
st.markdown("""
    <style>
    /* Remover padding superior da página */
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    
    /* Fundo Principal */
    .stApp { background-color: #0F172A; color: #F8FAFC; }
    
    /* Estilo dos Cards (Métricas) */
    div[data-testid="stMetric"] {
        background-color: #1E293B;
        padding: 10px 20px;
        border-radius: 10px;
        border: 1px solid #2D3748;
    }
    
    /* Ajuste de fontes e cores das métricas */
    div[data-testid="stMetricLabel"] { color: #94A3B8 !important; font-size: 1rem !important; }
    div[data-testid="stMetricValue"] { color: #5BC0EB !important; font-size: 1.8rem !important; }

    /* Esconder o Menu e Footer do Streamlit para ganhar espaço */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Configuração para Impressão A4 Deitado */
    @media print {
        @page { size: A4 landscape; margin: 0; }
        .stApp { background-color: #0F172A !important; }
        .no-print { display: none; }
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Função de Dados (Mantida conforme seu original)
def load_data():
    columns = [
        'Cliente', 'Indicador', 'Categoria', 'Valor', 'Entrada', 
        'Idade', 'Segundo_Pagto', 'Data', 'País', 'Indicação_Kalil',
        'Doc enviado', 'Doc Recebido', 'Comissão Larissa', 'telefone'
    ]
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

# Tratamento básico
numeric_cols = ['Valor', 'Entrada', 'Segundo_Pagto']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
df['Saldo'] = df['Valor'] - (df['Entrada'] + df['Segundo_Pagto'])
df['Total Pago'] = df['Entrada'] + df['Segundo_Pagto']

# 3. Interface Principal (Compacta)
st.title("📊 CRM Dashboard | Gestão Kalil")

# Métricas em uma única linha (6 colunas) para economizar espaço vertical
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Faturamento", f"R$ {df['Valor'].sum():,.0f}")
m2.metric("Total Pago", f"R$ {df['Total Pago'].sum():,.0f}")
m3.metric("Saldo", f"R$ {df['Saldo'].sum():,.0f}")
m4.metric("Vendas", len(df))
m5.metric("Conv.", f"{(len(df)/total_leads)*100:.1f}%" if 'total_leads' in locals() else "15%")
m6.metric("Público", df['Idade'].mode()[0])

# Configuração de cores Plotly baseada na imagem enviada
cores_mapa = ["#A05195", "#F9B24D", "#2F5D8C", "#665191", "#5BC0EB"]

# 4. Grid de Gráficos (Ajustado para 2x2 sem scroll)
c1, c2 = st.columns(2)
c3, c4 = st.columns(2)

with c1:
    fig_funil = px.funnel(pd.DataFrame({"E": ["Leads", "Vendas"], "Q": [40, len(df)]}), x='Q', y='E', 
                          title="Funil de Vendas", color_discrete_sequence=["#F9B24D", "#5BC0EB"])
    fig_funil.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#F8FAFC")
    st.plotly_chart(fig_funil, use_container_width=True)

with c2:
    fig_origem = px.bar(df.groupby("Indicador")["Valor"].sum().reset_index(), x="Valor", y="Indicador", orientation='h',
                        title="Faturamento por Canal", color="Indicador", color_discrete_sequence=cores_mapa)
    fig_origem.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#F8FAFC", showlegend=False)
    st.plotly_chart(fig_origem, use_container_width=True)

with c3:
    fig_cat = px.pie(df, values='Valor', names='Categoria', hole=.4, title="Mix de Categorias", color_discrete_sequence=cores_mapa)
    fig_cat.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', font_color="#F8FAFC")
    st.plotly_chart(fig_cat, use_container_width=True)

with c4:
    fig_idade = px.bar(df.groupby("Idade")["Valor"].sum().reset_index(), x="Idade", y="Valor", title="Faturamento/Idade",
                       color_discrete_sequence=["#A05195"])
    fig_idade.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#F8FAFC")
    st.plotly_chart(fig_idade, use_container_width=True)

# 5. Tabela Otimizada (Dentro de um Expander para não empurrar o layout se crescer)
with st.expander("📋 Ver Detalhamento de Clientes", expanded=True):
    st.dataframe(df[['Cliente', 'Categoria', 'Valor', 'Saldo', 'Doc enviado', 'Doc Recebido']], use_container_width=True, height=150)

# Botão Invisível para Impressão (Aparece apenas na tela)
st.sidebar.markdown("### 🖨️ Exportar")
if st.sidebar.button("Preparar para Foto/PDF (A4)"):
    st.markdown("<script>window.print();</script>", unsafe_allow_html=True)