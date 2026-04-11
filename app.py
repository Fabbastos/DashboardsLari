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

# --- Trecho Alterado: Linha de Métricas ---

# Cálculos de Faturamento por Canal
fat_lead = df[df['Canal'] == 'Lead']['Valor'].sum()
fat_kalil = df[df['Canal'] == 'Kalil']['Valor'].sum()
diff_fat = abs(fat_lead - fat_kalil)
vencedor = "Lead" if fat_lead > fat_kalil else "Kalil"

# Linha de Métricas (6 colunas atualizadas)
m1, m2, m3, m4, m5, m6 = st.columns(6)

with m1:
    st.metric("Faturamento LEAD", f"R$ {fat_lead:,.0f}")
with m2:
    st.metric("Faturamento KALIL", f"R$ {fat_kalil:,.0f}")
with m3:
    st.metric("Total Recebido", f"R$ {df['Total Pago'].sum():,.0f}")
with m4:
    st.metric("Saldo a Receber", f"R$ {df['Saldo'].sum():,.0f}")
with m5:
    st.metric("Vendas Fechadas", len(df))
with m6:
    st.metric(f"Vantagem ({vencedor})", f"R$ {diff_fat:,.0f}")

# ------------------------------------------
# --- Trecho Alterado: Estilização de Cores e Gráficos ---

# Definição da Paleta de Cores inspirada no Dashboard de RH (Dark Mode)
# Azul Claro (Lead/Ciano), Rosa Vibrante (Kalil/Roxo), Laranja (Destaque), Verde (Positivo), Vermelho (Alerta)
paleta_rh = ["#5BC0EB", "#A05195", "#F9B24D", "#27ae60", "#e74c3c"]

# Função para aplicar o estilo Dark mantendo o tamanho e cor das fontes
def aplicar_estilo_dark_com_fontes_originais(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', # Fundo transparente
        plot_bgcolor='rgba(0,0,0,0)',  # Fundo transparente
        font=dict(color="#FFFFFF", size=13), # Fonte BRANCA e MAIOR (13px)
        title_font=dict(color="#FFFFFF", size=16, family="Arial Black"), # Título maior e negrito
        margin=dict(l=10, r=10, t=40, b=10), # Margens apertadas para single-page
        # Legenda horizontal branca e maior
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=12, color="#FFFFFF"))
    )
    # Eixos com linhas de grade discretas e fontes de ticket brancas/maiores
    fig.update_xaxes(gridcolor='#1E293B', zerolinecolor='#1E293B', tickfont=dict(color="#FFFFFF", size=12))
    fig.update_yaxes(gridcolor='#1E293B', zerolinecolor='#1E293B', tickfont=dict(color="#FFFFFF", size=12))
    return fig

# --- Aplicação nos Gráficos ---

# 1. FUNIL COMPARATIVO (Barras agrupadas em funil)
# ... (cálculos do df_funil permanecem iguais)
fig1 = px.funnel(df_funil, x='Qtd', y='Etapa', color='Origem', 
                 title="Conversão por Canal", color_discrete_sequence=[paleta_rh[0], paleta_rh[1]])
fig1 = aplicar_estilo_dark_com_fontes_originais(fig1)
# Garante que os números dentro do funil também sejam brancos e legíveis
fig1.update_traces(textfont=dict(color="#FFFFFF", size=14, family="Arial Black"))
st.plotly_chart(fig1, use_container_width=True)


# 2. MIX DE PRODUTOS (Treemap - Barras retangulares)
# Substituiu a pizza de Mix de Produtos
fig2 = px.treemap(df, path=['Categoria'], values='Valor', title="Proporção por Produto (Treemap)",
                  color_discrete_sequence=paleta_rh) # Usa a paleta completa
fig2.update_layout(margin=dict(t=35, l=10, r=10, b=10), paper_bgcolor='rgba(0,0,0,0)', 
                   font=dict(color="white"), height=chart_height)
# Treemap não usa aplicar_estilo_dark, pois seu comportamento de fonte é diferente
st.plotly_chart(fig2, use_container_width=True)


# 3. FATURAMENTO POR IDADE E CANAL (Barras agrupadas)
# ... (agrupamento do df permanece igual)
fig3 = px.bar(df.groupby(["Idade", "Canal"])["Valor"].sum().reset_index(), 
              x="Idade", y="Valor", color="Canal", title="Faturamento por Idade",
              color_discrete_sequence=[paleta_rh[0], paleta_rh[1]], barmode='group')
st.plotly_chart(aplicar_estilo_dark_com_fontes_originais(fig3), use_container_width=True)


# 4. VENDAS POR PAÍS (Barras empilhadas)
# ... (agrupamento do df permanece igual)
fig4 = px.bar(df.groupby(["País", "Canal"])["Valor"].sum().reset_index(), 
              x="País", y="Valor", color="Canal", title="Faturamento por País",
              color_discrete_sequence=[paleta_rh[0], paleta_rh[1]])
# Afinamento de barras mantido (bargap)
fig4.update_layout(bargap=0.4) 
st.plotly_chart(aplicar_estilo_dark_com_fontes_originais(fig4), use_container_width=True)


# 5. STATUS DE DOCUMENTAÇÃO (Barras Horizontais)
# Substituiu a pizza de Documentação
fig5 = px.bar(df.groupby(["Doc_Status", "Canal"])["Valor"].count().reset_index(), 
              x="Valor", y="Doc_Status", color="Canal", orientation='h', 
              title="Documentos (Qtd Clientes)", color_discrete_sequence=[paleta_rh[0], paleta_rh[1]])
# Afinamento de barras mantido
fig5.update_layout(bargap=0.4) 
st.plotly_chart(aplicar_estilo_dark_com_fontes_originais(fig5), use_container_width=True)


# 6. SALDO A RECEBER (Barras por Cliente)
# ... (filtro do df devedor permanece igual)
fig6 = px.bar(df_devedor, x="Cliente", y="Saldo", color="Canal", 
              title="Saldo Devedor por Cliente", color_discrete_sequence=[paleta_rh[0], paleta_rh[1]])
# Afinamento de barras mantido
fig6.update_layout(bargap=0.4) 
st.plotly_chart(aplicar_estilo_dark_com_fontes_originais(fig6), use_container_width=True)

# ---------------------------------------------------