import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Executive CRM", layout="wide", page_icon="📊")

# =========================
# CSS ULTRA COMPACTO + DARK PRO
# =========================
st.markdown("""
<style>

/* ===== Tela inteira sem scroll ===== */
html, body, .stApp {
    height: 100vh;
    overflow: hidden;
    background-color: #020617;
    color: #E2E8F0;
}

/* container */
.block-container {
    padding: 0.4rem 1.2rem 0.4rem 1.2rem !important;
}

/* remover lixo visual */
#MainMenu, footer, header {
    display: none !important;
}

/* ===== Tipografia ===== */
h1, h2, h3 {
    margin: 0 !important;
    padding: 0 !important;
}

h2 {
    font-size: 1.1rem !important;
    font-weight: 600;
}

/* ===== MÉTRICAS ===== */
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #0F172A, #020617);
    padding: 6px 10px;
    border-radius: 10px;
    border: 1px solid #1E293B;
    box-shadow: 0 0 6px rgba(56,189,248,0.08);
}

/* label */
div[data-testid="stMetricLabel"] {
    font-size: 0.65rem !important;
    color: #94A3B8 !important;
}

/* valor */
div[data-testid="stMetricValue"] {
    font-size: 1rem !important;
    font-weight: 600;
    color: #38BDF8 !important;
}

/* espaçamento mínimo */
.element-container {
    margin-bottom: 0.15rem !important;
}

/* remover padding interno escondido */
.css-1kyxreq, .css-1d391kg {
    padding: 0 !important;
    margin: 0 !important;
}

</style>
""", unsafe_allow_html=True)

# =========================
# DATA
# =========================
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

# =========================
# CONFIG VISUAL
# =========================
chart_height = 150
paleta = ["#38BDF8", "#A855F7", "#F59E0B", "#22C55E", "#EF4444"]

def aplicar_estilo_dark(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#E2E8F0", size=11),
        margin=dict(l=5, r=5, t=25, b=5),
        height=chart_height,
        legend=dict(
            orientation="h",
            y=1.02,
            x=1,
            xanchor="right",
            font=dict(size=10)
        )
    )

    fig.update_xaxes(gridcolor='#1E293B', zerolinecolor='#1E293B')
    fig.update_yaxes(gridcolor='#1E293B', zerolinecolor='#1E293B')

    return fig

# =========================
# HEADER
# =========================
st.markdown("<h2>📊 Executive CRM</h2>", unsafe_allow_html=True)

# =========================
# KPIs
# =========================
fat_lead = df[df['Canal'] == 'Lead']['Valor'].sum()
fat_kalil = df[df['Canal'] == 'Kalil']['Valor'].sum()
diff = abs(fat_lead - fat_kalil)
winner = "Lead" if fat_lead > fat_kalil else "Kalil"

m1, m2, m3, m4, m5, m6 = st.columns(6)

m1.metric("LEAD", f"R$ {fat_lead:,.0f}")
m2.metric("KALIL", f"R$ {fat_kalil:,.0f}")
m3.metric("Recebido", f"R$ {df['Total Pago'].sum():,.0f}")
m4.metric("Saldo", f"R$ {df['Saldo'].sum():,.0f}")
m5.metric("Vendas", len(df))
m6.metric(f"Win ({winner})", f"R$ {diff:,.0f}")

# =========================
# LINHA 1
# =========================
c1, c2, c3 = st.columns(3)

with c1:
    df_funil = pd.DataFrame({
        'Etapa': ['Contatos', 'Vendas', 'Contatos', 'Vendas'],
        'Origem': ['Lead', 'Lead', 'Kalil', 'Kalil'],
        'Qtd': [40, len(df[df['Canal']=='Lead']), 12, len(df[df['Canal']=='Kalil'])]
    })

    fig1 = px.funnel(df_funil, x='Qtd', y='Etapa', color='Origem',
                     color_discrete_sequence=[paleta[0], paleta[1]])
    st.plotly_chart(aplicar_estilo_dark(fig1), use_container_width=True)

with c2:
    df_cat = df.groupby("Categoria")["Valor"].sum().reset_index()

    fig2 = px.bar(df_cat, x="Valor", y="Categoria",
                  orientation='h',
                  color_discrete_sequence=[paleta[2]])

    st.plotly_chart(aplicar_estilo_dark(fig2), use_container_width=True)

with c3:
    fig3 = px.bar(
        df.groupby(["Idade", "Canal"])["Valor"].sum().reset_index(),
        x="Idade", y="Valor", color="Canal",
        barmode='group',
        color_discrete_sequence=[paleta[0], paleta[1]]
    )

    st.plotly_chart(aplicar_estilo_dark(fig3), use_container_width=True)

# =========================
# LINHA 2
# =========================
c4, c5, c6 = st.columns(3)

with c4:
    fig4 = px.bar(
        df.groupby(["País", "Canal"])["Valor"].sum().reset_index(),
        x="País", y="Valor", color="Canal",
        color_discrete_sequence=[paleta[0], paleta[1]]
    )

    st.plotly_chart(aplicar_estilo_dark(fig4), use_container_width=True)

with c5:
    fig5 = px.bar(
        df.groupby(["Doc_Status", "Canal"])["Valor"].count().reset_index(),
        x="Valor", y="Doc_Status",
        orientation='h',
        color="Canal",
        color_discrete_sequence=[paleta[0], paleta[1]]
    )

    st.plotly_chart(aplicar_estilo_dark(fig5), use_container_width=True)

with c6:
    df_dev = df[df['Saldo'] > 0]

    fig6 = px.bar(
        df_dev,
        x="Cliente", y="Saldo",
        color="Canal",
        color_discrete_sequence=[paleta[0], paleta[1]]
    )

    st.plotly_chart(aplicar_estilo_dark(fig6), use_container_width=True)