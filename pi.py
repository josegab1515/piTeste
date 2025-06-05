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
        "irrigador": "Aspersor",
        "timestamp": "Horário"
    }, inplace=True)

    df["Horário"] = pd.to_datetime(df["Horário"])
    df = df.sort_values("Horário")

    # Transformar coluna Aspersor em texto 
    df["Aspersor"] = df["Aspersor"].map({True: "Ligado", False: "Desligado"})

    #Resumo
    st.subheader("Resumo")
    dispositivo_atual = df["Dispositivo"].iloc[-1]
    umidade_atual = df["Umidade"].iloc[-1]
    status_atual = df["Aspersor"].iloc[-1]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Dispositivo", dispositivo_atual)
    with col2:
        st.metric("Umidade Atual (%)", f"{umidade_atual:.2f}")
    with col3:
        st.metric("Aspersor", status_atual)

    st.markdown("---")

    # Dados Coletados
    st.subheader("Dados Coletados")
    st.dataframe(df)
    st.markdown("---")

    # Gráficos
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Umidade por Dispositivo")
        umidade_media = df.groupby("Dispositivo")["Umidade"].mean()
        fig_bar, ax_bar = plt.subplots(figsize=(6, 4))
        ax_bar.bar(umidade_media.index, umidade_media.values, color="#69b3a2")
        ax_bar.set_xlabel("Dispositivo")
        ax_bar.set_ylabel("Umidade Média (%)")
        ax_bar.set_title("Umidade Média por Dispositivo")
        st.pyplot(fig_bar)
    with col2:
        st.markdown("### Histórico de Umidade")
        fig_line, ax_line = plt.subplots(figsize=(8, 4))
        ax_line.plot(df["Horário"], df["Umidade"], marker="o", color="#0077b6")
        ax_line.set_xlabel("Horário")
        ax_line.set_ylabel("Umidade (%)")
        ax_line.set_title(f"Variação da Umidade — {dispositivo_atual}")
        plt.xticks(rotation=45)
        st.pyplot(fig_line)

    st.markdown("---")

    # Status detalhado dos dispositivos
    st.subheader("Status Detalhado dos Dispositivos")
    num_colunas = 3
    colunas = st.columns(num_colunas)

    for i, (_, row) in enumerate(df.iterrows()):
        with colunas[i % num_colunas]:
            ligado_texto = row["Aspersor"]
            ligado_cor = "#4CAF50" if ligado_texto == "Ligado" else "#F44336"

            st.markdown(f"### {row['Dispositivo']}")
            st.progress(row["Umidade"] / 100)
            st.markdown(f"**Umidade:** {row['Umidade']}%")
            st.markdown(
                f"<span style='color:{ligado_cor}; font-weight:bold;'>{ligado_texto}</span>", 
                unsafe_allow_html=True
            )
else:
    st.warning("Nenhum dado carregado da API.")
