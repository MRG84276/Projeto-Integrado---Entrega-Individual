import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np


st.set_page_config(
    page_title="Dashboard - Curso Superior - IBGE",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.title("Curso Superior")
st.markdown("---")
st.title("Dashboard de Visualização de Dados")
st.markdown("Análise visual das métricas acadêmicas e operacionais.")
st.markdown("Fonte: **SIDRA - Censo Demográfico 2022 — IBGE (Tabelas 10064 e 10065)**")
st.markdown("---")


@st.cache_data
def carregar_dados():
    df_65 = pd.read_csv("tabela10065.csv", sep=";", skiprows=4)
    sudeste_states = ['Minas Gerais', 'Espírito Santo', 'Rio de Janeiro', 'São Paulo']
    df_sudeste_65 = df_65[df_65.iloc[:, 0].isin(sudeste_states) & (df_65.iloc[:, 1] == "Total")].copy()
    df_64 = pd.read_csv("tabela10064.csv", sep=";", skiprows=4)
    df_sudeste_64 = df_64[df_64.iloc[:, 0].isin(sudeste_states)].copy()
    
    return df_sudeste_65, df_sudeste_64

df_ibge_65, df_ibge_64 = carregar_dados()

st.sidebar.header("Filtros do Dashboard")

sudeste_states = ['Minas Gerais', 'Espírito Santo', 'Rio de Janeiro', 'São Paulo']

uf_selecionada = st.sidebar.multiselect(
    "Selecione os Estados (Sudeste):",
    options=sudeste_states,
    default=sudeste_states
)

if not df_ibge_65.empty:
    col_uf = df_ibge_65.columns[0]
    col_total = df_ibge_65.columns[2]
    df_ibge_65[col_total] = pd.to_numeric(df_ibge_65[col_total].str.replace('.', '', regex=False), errors='coerce')

    st.subheader("Panorama Geral do Ensino Superior no Sudeste (Tabela 10065)")
    cols = st.columns(len(df_ibge_65))
    for idx, row in df_ibge_65.iterrows():
        uf_nome = row[col_uf]
        total_grad = row[col_total]
        with cols[list(df_ibge_65.index).index(idx)]:
            st.metric(label=uf_nome, value=f"{total_grad:,.0f} pessoas".replace(',', '.'))
            
    st.markdown("---")
    
if not df_totais_uf.empty:
        total_geral_sudeste = df_totais_uf[col_total].sum()
        media_sudeste = df_totais_uf[col_total].mean()
        maior_uf = df_totais_uf.loc[df_totais_uf[col_total].idxmax()]
        menor_uf = df_totais_uf.loc[df_totais_uf[col_total].idxmin()]

        st.subheader("Indicadores Dinâmicos Regionais")
        col1, col2, col33, col4 = st.columns(4)
        
        with col1:
            st.metric(label="Média Regional (Sudeste)", value=f"{media_sudeste:,.0f} pes.".replace(',', '.'))
        with col2:
            st.metric(label=f"Maior Estado ({maior_uf[col_uf]})", value=f"{maior_uf[col_total]:,.0f}".replace(',', '.'))
        with col3:
            st.metric(label=f"Menor Estado ({menor_uf[col_uf]})", value=f"{menor_uf[col_total]:,.0f}".replace(',', '.'))
        with col4:
            st.metric(label="Total Acumulado Selecionado", value=f"{total_geral_sudeste:,.0f}".replace(',', '.'))

    st.divider()

    st.sidebar.markdown("---")
    racas_disponiveis = df_65[col_raca].dropna().unique().tolist()
    raca_selecionada = st.sidebar.selectbox("Filtrar Recorte de Raça/Cor:", options=["Todas"] + [r for r in racas_disponiveis if r != "Total"])

    df_raca_filtrado = df_sudeste_65[df_sudeste_65[col_raca] != "Total"]
    if raca_selecionada != "Todas":
        df_raca_filtrado = df_raca_filtrado[df_raca_filtrado[col_raca] == raca_selecionada]

    st.subheader("Recorte Demográfico por Raça/Cor (Tabela 10065)")
    if not df_raca_filtrado.empty:
        fig_raca = px.bar(
            df_raca_filtrado,
            x=col_uf,
            y=col_total,
            color=col_raca,
            barmode="group",
            title="Distribuição por Cor ou Raça nos Estados Selecionados",
            labels={col_total: "População", col_uf: "Estado", col_raca: "Raça/Cor"}
        )
        st.plotly_chart(fig_raca, use_container_width=True)

if not df_64.empty:
    st.divider()
    st.subheader("Perfil Etário do Ensino Superior (Tabela 10064)")
    
    col_uf_64 = df_64.columns[0]
    col_idade = df_64.columns[1]
    col_total_64 = df_64.columns[2]
    
    df_sudeste_64 = df_64[df_64[col_uf_64].isin(uf_selecionada)].copy()
    df_sudeste_64[col_total_64] = pd.to_numeric(df_sudeste_64[col_total_64].astype(str).str.replace('.', '', regex=False), errors='coerce')

    df_faixas = df_sudeste_64[df_sudeste_64[col_idade] != "Total"]
    
    if not df_faixas.empty:
        fig_idade = px.bar(
            df_faixas,
            x=col_uf_64,
            y=col_total_64,
            color=col_idade,
            barmode="group",
            title="População com Superior Completo por Grupo de Idade",
            labels={col_total_64: "Pessoas", col_uf_64: "Estado", col_idade: "Faixa Etária"}
        )
        st.plotly_chart(fig_idade, use_container_width=True)
        
    with st.expander("Ver Tabela Bruta de Dados Filtrados"):
        st.dataframe(df_sudeste_64, use_container_width=True, hide_index=True)


st.subheader("📐 Estatísticas Descritivas e Indicadores Avançados")

# Substituição do np.random por dados reais extraídos de df_totais_uf (População com Superior por Estado filtrado)
if not df_totais_uf.empty:
    serie_valores = df_totais_uf[col_total]
else:
    serie_valores = pd.Series([0])

media = serie_valores.mean()
mediana = serie_valores.median()
q1 = serie_valores.quantile(0.25)
q3 = serie_valores.quantile(0.75)
iqr = q3 - q1
desvio_padrao = serie_valores.std()
variancia = serie_valores.var()

col4, col5, col6 = st.columns(3)

with col4:
    fig_box = px.box(df_totais_uf, y=col_total, title='Distribuição e Quartis (Boxplot)', labels={col_total: 'População Graduada'})
    st.plotly_chart(fig_box, use_container_width=True)

with col5:
    fig_hist = px.histogram(df_totais_uf, x=col_total, nbins=len(df_totais_uf), title='Frequência por Estado', labels={col_total: 'População Graduada'})
    st.plotly_chart(fig_hist, use_container_width=True)

with col6:
    fig_horizontal = px.bar(
        df_totais_uf,
        x=col_total,
        y=col_uf,
        orientation='h',
        text=col_total,
        color=col_uf,
        color_discrete_sequence=px.colors.sequential.Blues_r,
        title="Total de Pessoas com Nível Superior Completo por Estado",
        labels={col_total: "Pessoas Graduadas", col_uf: "Unidade da Federação"}
    )
    
    fig_horizontal.update_traces(
        texttemplate='%{text:,.0f}', 
        textposition='outside'
    )
    
    fig_horizontal.update_layout(
        xaxis_title="População com Superior Completo",
        yaxis_title="Estado",
        showlegend=False
    )
    
    st.plotly_chart(fig_horizontal, use_container_width=True)

st.success(f"""
**Análise dos Dados Reais - Medidas de Tendência Central e Dispersão:**
- **Tendência Central:** A **média** de **{media:,.0f}** pessoas e a **mediana** de **{mediana:,.0f}** refletem a realidade demográfica e o impacto concentrador dos estados selecionados.
- **Dispersão:** O **desvio padrão** de **{desvio_padrao:,.0f}** evidencia a heterogeneidade e a disparidade populacional entre as unidades da federação.
- **Quartis e IQR:** O intervalo interquartil (**IQR = {iqr:,.0f}**) delimita a faixa central de variação dos estados analisados.
""")

st.divider()

st.subheader("📋 Tabela Completa de Indicadores (Extraída das Tabelas do Censo)")


if not df_totais_uf.empty:
    df_estados_tabela = df_totais_uf[[col_uf, col_total]].copy()
    df_estados_tabela.columns = ["Recorte", "Total Absoluto"]
    df_estados_tabela.insert(0, "Categoria", "Unidade da Federação")
    
    
    if 'dados_raca' in locals() and not dados_raca.empty:
        df_raca_tabela = dados_raca.copy()
        df_raca_tabela.columns = ["Recorte", "Percentual(%)"]
        df_raca_tabela.insert(0, "Categoria", "Raça/Cor")
        
        
        df_completo = pd.concat([df_estados_tabela, df_raca_tabela], ignore_index=True, sort=False)
    else:
        df_completo = df_estados_tabela
else:
    df_completo = pd.DataFrame(columns=["Categoria", "Recorte", "Total Absoluto"])

categoria_selecionada = st.selectbox("Filtrar tabela por categoria:", ["Todas"] + list(df_completo["Categoria"].unique()))

if categoria_selecionada != "Todas":
    df_filtrado = df_completo[df_completo["Categoria"] == categoria_selecionada]
else:
    df_filtrado = df_completo

st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
