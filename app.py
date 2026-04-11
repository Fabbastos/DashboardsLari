import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Executive CRM", layout="wide")

# --- CORES IDENTIDADE ---
COLOR_LEAD, COLOR_KALIL, TEXT_COLOR = "#5BC0EB", "#A05195", "#FFFFFF"
PALETA_MAP = {"Lead": COLOR_LEAD, "Kalil": COLOR_KALIL}

# --- CSS ULTRA COMPACTO (Com remoção de botões nativos) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0F172A; }}
    .block-container {{ padding: 0.2rem 1rem 0rem 1rem !important; }}
    
    /* ESCONDER BOTÕES NATIVOS (Manage App, Menu, Footer) */
    header {{ visibility: hidden; height: 0px; }}
    footer {{ visibility: hidden; }}
    #MainMenu {{ visibility: hidden; }}
    .stDeployButton {{ display:none; }}
    [data-testid="stToolbar"] {{ visibility: hidden; }}
    [data-testid="stDecoration"] {{ display:none; }}
    
    .main-title {{ 
        font-size: 1.2rem !important; 
        font-weight: bold; 
        margin: 0px 0px 10px 0px !important; 
        color: white;
    }}
    
    .channel-label {{
        font-size: 1.1rem !important;
        font-weight: 800 !important;
        margin-bottom: 5px !important;
        margin-top: 5px !important;
        letter-spacing: 1px;
        text-transform: uppercase;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        display: inline-block;
        width: 100%;
    }}

    div[data-testid="stMetric"] {{
        background-color: #1E293B;
        padding: 2px 10px !important;
        border: 1px solid #334155;
        height: 50px !important;
        margin-bottom: 2px !important;
    }}
    div[data-testid="stMetricLabel"] {{ font-size: 0.75rem !important; color: #CBD5E1 !important; margin-bottom: -15px; }}
    div[data-testid="stMetricValue"] {{ font-size: 1.1rem !important; font-weight: bold; color: white !important; }}

    hr {{ margin: 8px 0px !important; opacity: 0.1; }}
    [data-testid="column"] {{ padding: 0px 5px !important; }}
    </style>
    """, unsafe_allow_html=True)

# 2. Dados
def load_data():
    columns = ['Cliente', 'Canal', 'Categoria', 'Valor', 'Entrada', 'Idade', 'Segundo_Pagto', 'País', 'Doc_Status']
    data = [
        ['Ana Silva', 'Lead', 'ID-DEFINITIVO', 5000, 2500, '20-25', 1000, 'Brasil', 'Ok'],
        ['Bruno Costa', 'Kalil', 'TRC PROV.', 1500, 500, '31-35', 0, 'Portugal', 'Pendente'],
        ['Carla Souza', 'Lead', 'AE TODAS', 4500, 4500, '40-45', 0, 'Brasil', 'Ok'],
        ['Diego Lima', 'Kalil', 'AB CARRO', 8000, 4000, '31-35', 2000, 'Angola', 'Pendente'],
        ['Erik Rocha', 'Lead', 'Carta AE', 6000, 3000, '26-30', 1000, 'Brasil', 'Ok'],
        ['Fernanda Luz', 'Lead', 'Renov. CNH', 1200, 1200, '50-55', 0, 'Portugal', 'Ok'],
    ]
    df = pd.DataFrame(data, columns=columns)
    df['Total Pago'] = df['Entrada'] + df['Segundo_Pagto']
    df['Saldo'] = df['Valor'] - df['Total Pago']
    return df

df = load_data()

def aplicar_estilo_dashboard(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=TEXT_COLOR, size=11),
        title_font=dict(color=TEXT_COLOR, size=14, family="Arial Black"),
        margin=dict(l=10, r=10, t=35, b=5),
        height=190, 
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10))
    )
    fig.update_xaxes(title="", gridcolor='#1E293B', tickfont=dict(size=10))
    fig.update_yaxes(title="", gridcolor='#1E293B', tickfont=dict(size=10))
    fig.update_traces(textfont_color="white") 
    return fig

# 3. Layout Principal
st.markdown('<p class="main-title">📊 Executive CRM Dashboard</p>', unsafe_allow_html=True)

def get_metrics(channel):
    subset = df[df['Canal'] == channel]
    return {
        "fat": subset['Valor'].sum(),
        "pago": subset['Total Pago'].sum(),
        "saldo": subset['Saldo'].sum(),
        "ticket": subset['Valor'].mean() if len(subset) > 0 else 0
    }

l_m = get_metrics('Lead')
k_m = get_metrics('Kalil')

# --- MÉRICAS LEAD ---
st.markdown(f"<p class='channel-label' style='color:{COLOR_LEAD}'>LEAD</p>", unsafe_allow_html=True)
l1, l2, l3, l4 = st.columns(4)
l1.metric("Faturamento", f"R$ {l_m['fat']:,.0f}")
l2.metric("Total Pago", f"R$ {l_m['pago']:,.0f}")
l3.metric("Saldo", f"R$ {l_m['saldo']:,.0f}")
l4.metric("Ticket Médio", f"R$ {l_m['ticket']:,.0f}")

# --- MÉRICAS KALIL ---
st.markdown(f"<p class='channel-label' style='color:{COLOR_KALIL}'>KALIL</p>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
k1.metric("Faturamento", f"R$ {k_m['fat']:,.0f}")
k2.metric("Total Pago", f"R$ {k_m['pago']:,.0f}")
k3.metric("Saldo", f"R$ {k_m['saldo']:,.0f}")
k4.metric("Ticket Médio", f"R$ {k_m['ticket']:,.0f}")

st.markdown("<hr>", unsafe_allow_html=True)

# --- GRÁFICOS ---
c1, c2, c3 = st.columns(3)
with c1:
    df_funil = pd.DataFrame({
        'Etapa': ['Contatos', 'Clientes', 'Contatos', 'Clientes'],
        'Canal': ['Lead', 'Lead', 'Kalil', 'Kalil'],
        'Qtd': [40, 4, 12, 2]
    })
    fig1 = px.funnel(df_funil, x='Qtd', y='Etapa', color='Canal', title="Conversão", color_discrete_map=PALETA_MAP)
    fig1.update_traces(textinfo="value", textfont=dict(color="white", size=12))
    st.plotly_chart(aplicar_estilo_dashboard(fig1), use_container_width=True)

with c2:
    fig2 = px.bar(df.groupby("Categoria")["Valor"].sum().reset_index(), x="Valor", y="Categoria", orientation='h', title="Mix de Produtos (R$)", color_discrete_sequence=[COLOR_LEAD])
    st.plotly_chart(aplicar_estilo_dashboard(fig2), use_container_width=True)

with c3:
    df_idade_qtd = df.groupby(["Idade", "Canal"]).size().reset_index(name='Qtd')
    fig3 = px.bar(df_idade_qtd, x="Idade", y="Qtd", color="Canal", barmode='group', title="Qtd. Clientes por Idade", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_dashboard(fig3), use_container_width=True)

c4, c5, c6 = st.columns(3)
with c4:
    df_pais_qtd = df.groupby(["País", "Canal"]).size().reset_index(name='Qtd')
    fig4 = px.bar(df_pais_qtd, x="País", y="Qtd", color="Canal", barmode='group', title="Qtd. Clientes por País", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_dashboard(fig4), use_container_width=True)

with c5:
    fig5 = px.bar(df.groupby(["Idade", "Canal"])["Valor"].sum().reset_index(), x="Idade", y="Valor", color="Canal", barmode='group', title="Faturamento por Idade", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_dashboard(fig5), use_container_width=True)

with c6:
    fig6 = px.bar(df[df['Saldo'] > 0], x="Cliente", y="Saldo", color="Canal", title="Saldo Devedor por Cliente", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_dashboard(fig6), use_container_width=True)