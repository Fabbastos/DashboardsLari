import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página para evitar rolagem
st.set_page_config(page_title="Executive CRM Premium", layout="wide", page_icon="📊")

# --- CSS: Design Premium e Ajuste de Altura ---
st.markdown("""
    <style>
    /* Fundo e Fonte Global */
    .stApp { background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%); color: #FFFFFF; }
    
    /* ZERAR espaços para eliminar o corte inferior */
    .block-container { padding-top: 0.5rem !important; padding-bottom: 0rem !important; }
    header, footer { visibility: hidden !important; }
    
    /* Títulos Brancos e Premium */
    h2 { color: #FFFFFF !important; font-family: 'Inter', sans-serif; font-weight: 800; letter-spacing: -0.5px; }

    /* Cards de Métricas Estilo HR Analytics */
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    div[data-testid="stMetricLabel"] { color: #94A3B8 !important; font-size: 0.8rem !important; text-transform: uppercase; }
    div[data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 1.4rem !important; }

    /* Ajuste de espaçamento entre colunas de gráficos */
    [data-testid="column"] { padding: 0 5px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Dados de Exemplo (Mantidos para consistência)
@st.cache_data
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

# Paleta HR Analytics
paleta_rh = ["#5BC0EB", "#A05195", "#F9B24D", "#27ae60", "#e74c3c"]
CHART_HEIGHT = 215 # Reduzido ligeiramente para garantir que não corte em baixo

# 3. Cabeçalho e Métricas
st.markdown("<h2 style='margin-bottom: 15px;'>EXECUTIVE CRM <span style='color:#5BC0EB'>| DASHBOARD</span></h2>", unsafe_allow_html=True)

fat_lead = df[df['Canal'] == 'Lead']['Valor'].sum()
fat_kalil = df[df['Canal'] == 'Kalil']['Valor'].sum()
diff_fat = abs(fat_lead - fat_kalil)
vencedor = "Lead" if fat_lead > fat_kalil else "Kalil"

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Faturamento Lead", f"R$ {fat_lead:,.0f}")
m2.metric("Faturamento Kalil", f"R$ {fat_kalil:,.0f}")
m3.metric("Total Recebido", f"R$ {df['Total Pago'].sum():,.0f}")
m4.metric("Saldo a Receber", f"R$ {df['Saldo'].sum():,.0f}")
m5.metric("Vendas Fechadas", len(df))
m6.metric(f"Vantagem ({vencedor})", f"R$ {diff_fat:,.0f}")

# 4. Função de Estilo Plotly Premium
def style_chart(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#FFFFFF", size=11),
        title_font=dict(color="#FFFFFF", size=14, family="Arial Black"),
        margin=dict(l=10, r=10, t=35, b=0), # Margem inferior zerada
        height=CHART_HEIGHT,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10))
    )
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.05)', zeroline=False)
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.05)', zeroline=False)
    return fig

# 5. Layout de Gráficos (2 fileiras de 3)
st.write("") 
c1, c2, c3 = st.columns(3)

with c1:
    df_funil = pd.DataFrame({
        'Etapa': ['1. Leads', '2. Vendas', '1. Leads', '2. Vendas'],
        'Canal': ['Lead', 'Lead', 'Kalil', 'Kalil'],
        'Qtd': [40, 4, 12, 2] # Dados do funil anterior
    })
    fig1 = px.funnel(df_funil, x='Qtd', y='Etapa', color='Canal', title="Conversão por Canal", color_discrete_sequence=[paleta_rh[0], paleta_rh[1]])
    st.plotly_chart(style_chart(fig1), use_container_width=True)

with c2:
    fig2 = px.bar(df.groupby("Categoria")["Valor"].sum().reset_index().sort_values("Valor"), 
                  x="Valor", y="Categoria", orientation='h', title="Mix de Produtos", color_discrete_sequence=[paleta_rh[2]])
    fig2.update_layout(bargap=0.5)
    st.plotly_chart(style_chart(fig2), use_container_width=True)

with c3:
    fig3 = px.bar(df.groupby(["Idade", "Canal"])["Valor"].sum().reset_index(), 
                  x="Idade", y="Valor", color="Canal", title="Faturamento por Idade", color_discrete_sequence=[paleta_rh[0], paleta_rh[1]], barmode='group')
    fig3.update_layout(bargap=0.4)
    st.plotly_chart(style_chart(fig3), use_container_width=True)

c4, c5, c6 = st.columns(3)

with c4:
    fig4 = px.bar(df.groupby(["País", "Canal"])["Valor"].sum().reset_index(), x="País", y="Valor", color="Canal", title="Vendas por País", color_discrete_sequence=[paleta_rh[0], paleta_rh[1]])
    fig4.update_layout(bargap=0.4)
    st.plotly_chart(style_chart(fig4), use_container_width=True)

with c5:
    fig5 = px.bar(df.groupby(["Doc_Status", "Canal"])["Valor"].count().reset_index(), x="Valor", y="Doc_Status", color="Canal", orientation='h', title="Documentação", color_discrete_sequence=[paleta_rh[0], paleta_rh[1]])
    fig5.update_layout(bargap=0.4)
    st.plotly_chart(style_chart(fig5), use_container_width=True)

with c6:
    fig6 = px.bar(df[df['Saldo'] > 0], x="Cliente", y="Saldo", color="Canal", title="Saldo Devedor", color_discrete_sequence=[paleta_rh[0], paleta_rh[1]])
    fig6.update_layout(bargap=0.4)
    st.plotly_chart(style_chart(fig6), use_container_width=True)