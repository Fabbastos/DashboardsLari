import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Executive CRM", layout="wide", page_icon="📊")

# --- CORES IDENTIDADE ---
COLOR_LEAD, COLOR_KALIL, TEXT_COLOR = "#8B4513", "#FFB347", "#FFFFFF"
PALETA_MAP = {"Lead": COLOR_LEAD, "Kalil": COLOR_KALIL}

# --- CSS RESPONSIVO ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0F172A; }}
    .block-container {{ padding: 1rem 1rem 5rem 1rem !important; }}
    
    /* Força cor branca em textos */
    h1, h2, h3, p, span {{ color: {TEXT_COLOR} !important; }}
    
    /* FIX FILTRO SELECTBOX */
    div[data-baseweb="select"] > div {{
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
    }}
    
    header {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    
    .main-title {{ font-size: 1.5rem !important; font-weight: bold; margin-bottom: 20px; }}
    .channel-label {{ font-size: 1.1rem !important; font-weight: 800 !important; margin-top: 10px; border-bottom: 2px solid rgba(255,255,255,0.1); width: 100%; }}

    /* MÉTRICAS */
    div[data-testid="stMetric"] {{ 
        background-color: #1E293B; 
        padding: 15px !important; 
        border: 1px solid #334155; 
        border-radius: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. Funções de Dados
SHEET_ID = "1mVcogReqnHTyzAes_NJYu0MBHEDbqyj1_suJMGOnf0Q"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = [c.strip() for c in df.columns]
        
        def clean_currency(value):
            if pd.isna(value): return 0.0
            if isinstance(value, (int, float)): return float(value)
            # Remove símbolos, espaços e ajusta separadores Europeus/Brasileiros
            clean_val = str(value).replace('€', '').replace('R$', '').strip()
            if '.' in clean_val and ',' in clean_val: # Formato 1.234,56
                clean_val = clean_val.replace('.', '').replace(',', '.')
            elif ',' in clean_val: # Formato 1234,56
                clean_val = clean_val.replace(',', '.')
            return pd.to_numeric(clean_val, errors='coerce') or 0.0

        cols_financeiras = ['Valor', 'Entrada', 'Segundo_Pagto']
        for col in cols_financeiras:
            if col in df.columns:
                df[col] = df[col].apply(clean_currency)
            else:
                df[col] = 0.0

        # Cálculos de Negócio
        df['Total Pago'] = df['Entrada'] + df['Segundo_Pagto']
        df['Saldo Total'] = df['Valor'] - df['Total Pago']
        
        # Lógica de classificação de pagamentos
        df['Pago Vista'] = df.apply(lambda x: x['Valor'] if x['Entrada'] >= x['Valor'] and x['Valor'] > 0 else 0, axis=1)
        df['Pago Parcelado'] = df.apply(lambda x: x['Total Pago'] if x['Entrada'] < x['Valor'] else 0, axis=1)
        df['Saldo Parcelado'] = df.apply(lambda x: x['Saldo Total'] if x['Entrada'] < x['Valor'] else 0, axis=1)
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df_base = load_data()

def aplicar_estilo(fig, is_bar=False):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=TEXT_COLOR, size=11), 
        margin=dict(l=10, r=10, t=40, b=10), 
        height=250,
        hovermode="closest", 
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    if is_bar:
        fig.update_xaxes(showgrid=False, zeroline=False)
        fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    return fig

if not df_base.empty:
    # --- CABEÇALHO ---
    head_col1, head_col2 = st.columns([3, 1])
    with head_col1:
        st.markdown('<p class="main-title">📊 Executive CRM Dashboard</p>', unsafe_allow_html=True)
    with head_col2:
        meses = ["Total"] + sorted([m for m in df_base['Mês'].unique() if pd.notna(m)])
        mes_filtro = st.selectbox("Filtrar Período", meses, label_visibility="collapsed")

    df = df_base if mes_filtro == "Total" else df_base[df_base['Mês'] == mes_filtro]
    df_vendas = df[df['Total Pago'] > 0].copy()

    # --- MÉTRICAS ---
    def render_metrics(channel, color):
        subset = df[df['Canal'] == channel]
        fat = subset['Valor'].sum()
        st.markdown(f"<p class='channel-label' style='color:{color}'>{channel.upper()}</p>", unsafe_allow_html=True)
        
        m1, m2, m3, m4 = st.columns(4)
        
        def fmt(val): return f"€ {val:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        def pct_label(p): return f"{(p / fat * 100):.1f}%" if fat > 0 else "0%"

        m1.metric("Faturamento Total", fmt(fat))
        
        v = subset['Pago Vista'].sum()
        m2.metric("À Vista", fmt(v), delta=pct_label(v))
        
        p = subset['Pago Parcelado'].sum()
        m3.metric("Pago (Parc.)", fmt(p), delta=pct_label(p))
        
        s = subset['Saldo Parcelado'].sum()
        m4.metric("Saldo a Receber", fmt(s), delta=pct_label(s), delta_color="inverse")

    render_metrics('Lead', COLOR_LEAD)
    render_metrics('Kalil', COLOR_KALIL)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # --- GRÁFICOS ---
    c1, c2, c3 = st.columns(3)

    with c1:
        fd = []
        for c in ["Lead", "Kalil"]:
            sub = df[df['Canal'] == c]
            fd.append({'Etapa': '1. Contatos', 'Canal': c, 'Qtd': len(sub)})
            fd.append({'Etapa': '2. Clientes', 'Canal': c, 'Qtd': len(sub[sub['Total Pago'] > 0])})
        fig1 = px.funnel(pd.DataFrame(fd), x='Qtd', y='Etapa', color='Canal', title="Conversão de Funil", color_discrete_map=PALETA_MAP)
        st.plotly_chart(aplicar_estilo(fig1), use_container_width=True)

    with c2:
        if not df_vendas.empty:
            mix = df_vendas.groupby("Categoria")["Valor"].sum().reset_index()
            fig2 = px.bar(mix, x="Valor", y="Categoria", orientation='h', title="Mix de Produtos (€)", color_discrete_sequence=[COLOR_KALIL])
            st.plotly_chart(aplicar_estilo(fig2, is_bar=True), use_container_width=True)
        else: st.info("Sem dados de vendas")

    with c3:
        if not df_vendas.empty:
            idade_df = df_vendas.groupby(["Idade", "Canal"]).size().reset_index(name='Qtd')
            fig3 = px.bar(idade_df, x="Idade", y="Qtd", color="Canal", barmode='group', title="Perfil por Idade", color_discrete_map=PALETA_MAP)
            st.plotly_chart(aplicar_estilo(fig3, is_bar=True), use_container_width=True)

    c4, c5, c6 = st.columns(3)
    with c4:
        if not df_vendas.empty:
            pais_df = df_vendas.groupby(["País", "Canal"]).size().reset_index(name='Qtd')
            fig4 = px.bar(pais_df, x="País", y="Qtd", color="Canal", title="Distribuição Geográfica", color_discrete_map=PALETA_MAP)
            st.plotly_chart(aplicar_estilo(fig4, is_bar=True), use_container_width=True)

    with c5:
        if not df_vendas.empty:
            fat_idade = df_vendas.groupby(["Idade", "Canal"])["Valor"].sum().reset_index()
            fig5 = px.bar(fat_idade, x="Idade", y="Valor", color="Canal", barmode='group', title="Faturamento por Idade", color_discrete_map=PALETA_MAP)
            st.plotly_chart(aplicar_estilo(fig5, is_bar=True), use_container_width=True)

    with c6:
        saldo_df = df_vendas[df_vendas['Saldo Total'] > 0].sort_values('Saldo Total', ascending=False).head(10)
        if not saldo_df.empty:
            fig6 = px.bar(saldo_df, x="Cliente", y="Saldo Total", color="Canal", title="Top 10 Saldos de Clientes", color_discrete_map=PALETA_MAP)
            st.plotly_chart(aplicar_estilo(fig6, is_bar=True), use_container_width=True)
        else: st.info("Não há saldos pendentes")

else:
    st.error("A base de dados está vazia ou não pôde ser carregada. Verifique o ID da planilha e as permissões de compartilhamento (Qualquer pessoa com o link).")