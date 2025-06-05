import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard de Irrigação", layout="wide")
st.markdown("# 💧 Dashboard de Irrigação Inteligente")


API_URL = "https://irrigacao-psi.vercel.app/api/dados"

@st.cache_data(ttl=60)
def carregar_dados():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except Exception as e:
        st.error(f"Erro ao acessar a API: {e}")
        return pd.DataFrame()

df = carregar_dados()

if not df.empty:
    df.rename(columns={
        "dispositivo": "Dispositivo",
        "umidade": "Umidade",
        "irrigador": "Ligado",
        "timestamp": "Horário"
    }, inplace=True)

    # Dividir em 2 grupos para teste alternando linhas
    df = df.reset_index(drop=True)
    df["Dispositivo_Teste"] = df.index.map(lambda x: "1" if x % 2 == 0 else "2")

    st.markdown("---")
    st.subheader("📋 Dados Coletados")
    st.dataframe(df.style.highlight_min(subset=["Umidade"], color="lightcoral"))

    # Gráficos - mantidos do exemplo anterior
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🌱 Umidade por Grupo Experimental")
        umidade_media = df.groupby("Dispositivo_Teste")["Umidade"].mean()
        fig_bar, ax_bar = plt.subplots(figsize=(6, 4))
        ax_bar.bar(umidade_media.index, umidade_media.values, color=["#69b3a2", "#40798c"])
        ax_bar.set_xlabel("Grupo")
        ax_bar.set_ylabel("Umidade Média (%)")
        ax_bar.set_title("Umidade Média por Grupo")
        st.pyplot(fig_bar)

    with col2:
        st.markdown("### 🔌 Status dos Irrigadores por Grupo")
        status_por_grupo = df.groupby("Dispositivo_Teste")["Ligado"].mean()
        labels = status_por_grupo.index.tolist()
        valores = status_por_grupo.values.tolist()
        cores = ["#76c893", "#f94144"]

        fig_pie, ax_pie = plt.subplots()
        ax_pie.pie(valores, labels=labels, autopct='%1.1f%%', startangle=90, colors=cores)
        ax_pie.axis('equal')
        st.pyplot(fig_pie)

    st.markdown("---")
    st.subheader("📟 Status Detalhado dos Dispositivos")

    # Exibir os dispositivos em cards organizados em colunas
    num_colunas = 3
    colunas = st.columns(num_colunas)
    for i, (_, row) in enumerate(df.iterrows()):
        with colunas[i % num_colunas]:
            ligado_texto = "Ligado" if row["Ligado"] else "Desligado"
            ligado_cor = "#4CAF50" if row["Ligado"] else "#F44336"  # verde ou vermelho
            st.markdown(f"### {row['Dispositivo']} (Grupo {row['Dispositivo_Teste']})")
            st.progress(row["Umidade"] / 100)  # barra visual de umidade
            st.markdown(f"**Umidade:** {row['Umidade']}%")
            st.markdown(f"<span style='color:{ligado_cor}; font-weight:bold;'>{ligado_texto}</span>", unsafe_allow_html=True)

else:
    st.warning("Nenhum dado carregado da API.")
