import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Executive CRM", layout="wide")

# --- CORES IDENTIDADE ---
COLOR_LEAD, COLOR_KALIL, TEXT_COLOR = "#5BC0EB", "#A05195", "#FFFFFF"
PALETA_MAP = {"Lead": COLOR_LEAD, "Kalil": COLOR_KALIL}

# --- CSS ULTRA COMPACTO ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0F172A; }}
    .block-container {{ padding: 0.2rem 1rem 0rem 1rem !important; }}
    header {{ visibility: hidden; height: 0px; }}
    footer {{ visibility: hidden; }}
    .stDeployButton {{ display:none; }}
    
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
    div[data-testid="stMetricLabel"] {{ font-size: 0.72rem !important; color: #CBD5E1 !important; margin-bottom: -15px; }}
    div[data-testid="stMetricValue"] {{ font-size: 1.0rem !important; font-weight: bold; color: white !important; }}

    hr {{ margin: 8px 0px !important; opacity: 0.1; }}
    [data-testid="column"] {{ padding: 0px 5px !important; }}
    </style>
    """, unsafe_allow_html=True)

# 2. Dados (Expandidos e com Lógica de Pagamento)
def load_data():
    columns = ['Cliente', 'Canal', 'Categoria', 'Valor', 'Entrada', 'Idade', 'Segundo_Pagto', 'País', 'Doc_Status']
    data = [
        ['Ana Silva', 'Lead', 'ID-DEFINITIVO', 5000, 5000, '20-25', 0, 'Brasil', 'Ok'],
        ['Bruno Costa', 'Kalil', 'TRC PROV.', 1500, 500, '31-35', 0, 'Portugal', 'Pendente'],
        ['Carla Souza', 'Lead', 'AE TODAS', 4500, 4500, '40-45', 0, 'Brasil', 'Ok'],
        ['Diego Lima', 'Kalil', 'AB CARRO', 8000, 4000, '31-35', 2000, 'Angola', 'Pendente'],
        ['Erik Rocha', 'Lead', 'Carta AE', 6000, 3000, '26-30', 1000, 'Brasil', 'Ok'],
        ['Fernanda Luz', 'Lead', 'Renov. CNH', 1200, 1200, '50-55', 0, 'Portugal', 'Ok'],
        ['Gabriel Mendes', 'Lead', 'ID-DEFINITIVO', 5200, 5200, '20-25', 0, 'Brasil', 'Ok'],
        ['Helena Ramos', 'Kalil', 'TRC PROV.', 1800, 900, '26-30', 400, 'Portugal', 'Pendente'],
        ['Igor Antunes', 'Lead', 'AE TODAS', 4500, 2000, '31-35', 500, 'Angola', 'Pendente'],
        ['Juliana Paes', 'Kalil', 'AB CARRO', 7500, 7500, '40-45', 0, 'EUA', 'Ok'],
        ['Kevin Oliveira', 'Lead', 'Carta AE', 6000, 3000, '20-25', 0, 'Brasil', 'Pendente'],
        ['Larissa Mano', 'Kalil', 'Renov. CNH', 1300, 650, '50-55', 100, 'Brasil', 'Ok'],
        ['Marcos Frota', 'Lead', 'ID-DEFINITIVO', 5000, 5000, '31-35', 0, 'Portugal', 'Ok'],
        ['Nathalia Dill', 'Kalil', 'AE TODAS', 4200, 2100, '26-30', 1000, 'Angola', 'Pendente'],
        ['Otávio Mesca', 'Lead', 'AB CARRO', 8500, 4000, '40-45', 2000, 'Brasil', 'Ok'],
        ['Patrícia Pillar', 'Kalil', 'Carta AE', 5800, 5800, '50-55', 0, 'EUA', 'Ok'],
        ['Ricardo Tozzi', 'Lead', 'Renov. CNH', 1200, 1200, '20-25', 0, 'Brasil', 'Ok'],
        ['Sabrina Sato', 'Kalil', 'ID-DEFINITIVO', 5100, 2500, '31-35', 1000, 'Portugal', 'Pendente'],
        ['Thiago Lacerda', 'Lead', 'TRC PROV.', 1700, 1700, '40-45', 0, 'Angola', 'Ok'],
        ['Ursula Corbero', 'Kalil', 'AE TODAS', 4600, 2300, '26-30', 0, 'EUA', 'Pendente'],
        ['Vitor Hugo', 'Lead', 'AB CARRO', 7900, 3900, '50-55', 1000, 'Brasil', 'Ok'],
        ['Wagner Moura', 'Kalil', 'Carta AE', 6200, 6200, '31-35', 0, 'Portugal', 'Ok'],
        ['Xuxa Meneghel', 'Lead', 'Renov. CNH', 1250, 1250, '50-55', 0, 'Brasil', 'Ok'],
        ['Yuri Marçal', 'Kalil', 'ID-DEFINITIVO', 5000, 1000, '20-25', 500, 'Angola', 'Pendente'],
        ['Zeca Pagode', 'Lead', 'AE TODAS', 4400, 4400, '40-45', 0, 'Brasil', 'Ok'],
        ['Aline Riscado', 'Kalil', 'AB CARRO', 8200, 4100, '26-30', 2000, 'EUA', 'Pendente'],
    ]
    df = pd.DataFrame(data, columns=columns)
    
    # Lógica de Separação
    df['Total Pago'] = df['Entrada'] + df['Segundo_Pagto']
    df['Saldo Total'] = df['Valor'] - df['Total Pago']
    
    # Se Entrada == Valor, é à vista. Senão, é parcelado.
    df['Pago Vista'] = df.apply(lambda x: x['Valor'] if x['Entrada'] == x['Valor'] else 0, axis=1)
    df['Pago Parcelado'] = df.apply(lambda x: x['Total Pago'] if x['Entrada'] < x['Valor'] else 0, axis=1)
    df['Saldo Parcelado'] = df.apply(lambda x: x['Saldo Total'] if x['Entrada'] < x['Valor'] else 0, axis=1)
    
    return df

df = load_data()

def aplicar_estilo_dashboard(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=TEXT_COLOR, size=11),
        title_font=dict(color=TEXT_COLOR, size=14, family="Arial Black"),
        margin=dict(l=10, r=10, t=35, b=5), height=190, showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10))
    )
    fig.update_xaxes(title="", gridcolor='#1E293B', tickfont=dict(size=10))
    fig.update_yaxes(title="", gridcolor='#1E293B', tickfont=dict(size=10))
    fig.update_traces(textfont_color="white") 
    return fig

# 3. Layout Principal
st.markdown('<p class="main-title">📊 Executive CRM Dashboard</p>', unsafe_allow_html=True)

def render_metrics(channel, color):
    subset = df[df['Canal'] == channel]
    st.markdown(f"<p class='channel-label' style='color:{color}'>{channel}</p>", unsafe_allow_html=True)
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Faturamento", f"R$ {subset['Valor'].sum():,.0f}")
    m2.metric("Pago à Vista", f"R$ {subset['Pago Vista'].sum():,.0f}")
    m3.metric("Pago Parcelado", f"R$ {subset['Pago Parcelado'].sum():,.0f}")
    m4.metric("Saldo Parcelado", f"R$ {subset['Saldo Parcelado'].sum():,.0f}")
    m5.metric("Saldo Total", f"R$ {subset['Saldo Total'].sum():,.0f}")

render_metrics('Lead', COLOR_LEAD)
render_metrics('Kalil', COLOR_KALIL)

st.markdown("<hr>", unsafe_allow_html=True)

# --- GRÁFICOS ---
c1, c2, c3 = st.columns(3)
with c1:
    df_funil = pd.DataFrame({'Etapa': ['Contatos', 'Clientes', 'Contatos', 'Clientes'], 'Canal': ['Lead', 'Lead', 'Kalil', 'Kalil'], 'Qtd': [120, 15, 80, 11]})
    fig1 = px.funnel(df_funil, x='Qtd', y='Etapa', color='Canal', title="Conversão", color_discrete_map=PALETA_MAP)
    fig1.update_traces(textinfo="value", textfont=dict(color="white", size=12))
    st.plotly_chart(aplicar_estilo_dashboard(fig1), use_container_width=True)

with c2:
    fig2 = px.bar(df.groupby("Categoria")["Valor"].sum().reset_index(), x="Valor", y="Categoria", orientation='h', title="Mix de Produtos (R$)", color_discrete_sequence=[COLOR_LEAD])
    st.plotly_chart(aplicar_estilo_dashboard(fig2), use_container_width=True)

with c3:
    fig3 = px.bar(df.groupby(["Idade", "Canal"]).size().reset_index(name='Qtd'), x="Idade", y="Qtd", color="Canal", barmode='group', title="Qtd. Clientes por Idade", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_dashboard(fig3), use_container_width=True)

c4, c5, c6 = st.columns(3)
with c4:
    fig4 = px.bar(df.groupby(["País", "Canal"]).size().reset_index(name='Qtd'), x="País", y="Qtd", color="Canal", barmode='group', title="Qtd. Clientes por País", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_dashboard(fig4), use_container_width=True)

with c5:
    fig5 = px.bar(df.groupby(["Idade", "Canal"])["Valor"].sum().reset_index(), x="Idade", y="Valor", color="Canal", barmode='group', title="Faturamento por Idade", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_dashboard(fig5), use_container_width=True)

with c6:
    fig6 = px.bar(df[df['Saldo Total'] > 0], x="Cliente", y="Saldo Total", color="Canal", title="Saldo Devedor por Cliente", color_discrete_map=PALETA_MAP)
    st.plotly_chart(aplicar_estilo_dashboard(fig6), use_container_width=True)