import streamlit as st
import pandas as pd
import plotly.express as px
from constants import json_files, question_type_map

def init():
    st.set_page_config(
        page_title="VLMs dashboard", page_icon="📊", layout="wide"
        )
    st.title("📊 Dashboard de Benchmark de VLMs")
    tab1, tab2 = st.tabs(["🔎 Visão geral", "📂 Análise individual"])

    if not json_files:
        st.warning("Nenhum arquivo de resultado encontrado no diretório atual.")
        st.stop()
    return tab1, tab2

tab1, tab2 = init()

with tab1:
    st.subheader("Visão geral dos experimentos")

    selected_files = st.multiselect(
        "Escolha um ou mais arquivos de experimento:", 
        json_files, 
        default=json_files,
        format_func=lambda x: x.split("\\")[-1],
    )

    if not selected_files:
        st.warning("Selecione pelo menos um arquivo para visualizar.")
        st.stop()

    dfs = []
    for f in selected_files:
        df_temp = pd.read_json(f)
        df_temp["arquivo"] = f.split("\\")[-1]
        df_temp['id'] = df_temp.index
        dfs.append(df_temp)

    df_all = pd.concat(dfs)

    df_all["percentual_frames"] = df_all.apply(
        lambda row: (row["frames_analyzed"] / row["total_frames"]) * 100,
        axis=1 # apply over lines instead columns
    )

    df_metrics = df_all.groupby("arquivo").agg(
        accuracy=("is_correct", "mean"),
        media_latency=("latency", "mean"),
        media_analyzed_frames=("percentual_frames", "mean")
    ).reset_index()
    df_metrics["accuracy"] *= 100

    df_metrics = df_metrics.sort_values(
        by='accuracy', 
        ascending=False
    )

    df_display = df_metrics.rename(columns={
        "arquivo": "Arquivo",
        "accuracy": "Acurácia (%)",
        "media_latency": "Latência Média (s)",
        "media_analyzed_frames": "Frames Vistos (%)"
    })

    df_all = df_all.round(2)
    df_display = df_display.round(2)

    st.dataframe(df_display)

    fig_box = px.box(df_all, x="arquivo", y="latency",
                     color="arquivo", points="all", 
                     hover_data=["id"],
                     title="Distribuição da latência por experimento",
                     labels={"latency": "Latência (s)", 
                             "arquivo":"Arquivo"})
    st.plotly_chart(fig_box)

    if "question_type" in df_all.columns:
        df_all["question_type"] = df_all["question_type"].map(question_type_map)
        acc_tipo = df_all.groupby(["arquivo", "question_type"])["is_correct"].mean().reset_index()
        acc_tipo["is_correct"] *= 100
        fig = px.bar(acc_tipo, x="question_type", y="is_correct",
                     color="arquivo", barmode="group",
                     title="Acurácia (%) por Tipo de Questão",
                     labels={"is_correct": "Acurácia (%)",
                             "question_type": "Tipo de questão"})
        st.plotly_chart(fig)

with tab2:
    st.subheader("Análise por arquivo")

    selected_file = st.selectbox(
        "Escolha o arquivo de experimento:",
        json_files,
        format_func=lambda x: x.split("\\")[-1],
    )

    df = pd.read_json(selected_file)
    df['id'] = df.index
    modelos = df["video_analyzer"].unique()

    if len(modelos) > 1:
        selected_modelo = st.selectbox("Escolha o modelo para análise:", modelos)
        df_modelo = df[df["video_analyzer"] == selected_modelo]
    else:
        selected_modelo = modelos[0]
        df_modelo = df

    accuracy = df_modelo["is_correct"].mean() * 100
    media_latency = df_modelo["latency"].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("✅ Acurácia", f"{accuracy:.2f}%")
    col2.metric("⏱️ Latência média", f"{media_latency:.2f} s")
    col3.metric("📝 Total de Questões", f"{len(df_modelo)}")

    st.subheader("Latência por Questão")
    st.write(
        f"Latência mínima: {df_modelo['latency'].min():.2f} s | "
        f"Máxima: {df_modelo['latency'].max():.2f} s | "
        f"Mediana: {df_modelo['latency'].median():.2f} s"
    )

    df_modelo = df_modelo.round(2)
    if "question_type" in df_modelo.columns:
        df_modelo["question_type"] = df_modelo["question_type"].map(question_type_map)
        fig = px.box(df_modelo, x="question_type", y="latency",
                     color="question_type", points="all",
                     title="Boxplot da latência por tipo de questão",
                     hover_data=["id"],
                     labels={"latency": "Latência (s)", "question_type": "Tipo de questão"})
    else:
        fig = px.box(df_modelo, y="latency", points="all",
                     title="Boxplot da latência por questão",
                     hover_data=["id"],
                     labels={"latency": "Latência (s)"})
    st.plotly_chart(fig)

    if "question_type" in df_modelo.columns:
        acc_tipo = df_modelo.groupby("question_type")["is_correct"].mean().reset_index()
        acc_tipo["is_correct"] *= 100
        fig = px.bar(acc_tipo, x="question_type", y="is_correct",
                     title="Acurácia (%) por tipo de questão",
                     labels={"is_correct": "Acurácia (%)", "question_type": "Tipo de Questão"})
        st.plotly_chart(fig)

    if "total_frames" in df_modelo.columns and "frames_analyzed" in df_modelo.columns:
        df_modelo["percentual_frames"] = (
            df_modelo["frames_analyzed"] / df_modelo["total_frames"]
        ) * 100
        fig = px.histogram(df_modelo, x="percentual_frames", nbins=20,
                           title="Distribuição do percentual de frames analisados",
                           labels={"percentual_frames":"Percentual de frames analisados"})
        st.plotly_chart(fig)
