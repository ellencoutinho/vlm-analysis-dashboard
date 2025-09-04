import streamlit as st
import pandas as pd
import plotly.express as px
import glob

# Colunas do dataset:
# class BenchmarkItem:
#     video: bytes
#     question: str
#     question_type: str
#     options: list[str]
#     answer: str
#     video_path: Path
#     total_frames: float

# TODO: Adicionar comparativo de modelos como página principal, adicionar aba secundária
#       para focar a análise em um modelo específico.

st.title("📊 Dashboard de Benchmark de VLMs")

# Procurar todos os arquivos de resultados
json_files = glob.glob("runs/*.json")

if not json_files:
    st.warning("Nenhum arquivo de resultado encontrado no diretório atual.")
    st.stop()

# Barra lateral para selecionar o experimento
st.sidebar.header("Seleção de Experimento")
selected_file = st.sidebar.selectbox("Escolha o arquivo de experimento:", json_files)

# Carregar o dataset escolhido
df = pd.read_json(selected_file)

modelos = df["video_analyzer"].unique()

if len(modelos) > 1:
    selected_modelo = st.sidebar.selectbox("Escolha o modelo para análise:", modelos)
    df_modelo = df[df["video_analyzer"] == selected_modelo]
else:
    selected_modelo = modelos[0]
    df_modelo = df[df["video_analyzer"] == selected_modelo]


# Métricas principais
accuracy = df_modelo["is_correct"].mean() * 100
media_latency = df_modelo["latency"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("✅ Acurácia", f"{accuracy:.2f}%")
col2.metric("⏱️ Latência média", f"{media_latency:.2f} s")
col3.metric("📝 Total de Questões", f"{len(df_modelo)}")

# Latência por questão
st.subheader("Latência por Questão")
st.write(f"Latência mínima: {df_modelo['latency'].min():.2f} s | máxima: {df_modelo['latency'].max():.2f} s | mediana: {df_modelo['latency'].median():.2f} s")
if "question_type" in df_modelo.columns:
    fig = px.box(df_modelo, x="question_type", y="latency", color="question_type", points="all", title="Boxplot da Latência por Tipo de Questão")
else:
    fig = px.box(df_modelo, y="latency", points="all", title="Boxplot da Latência por Questão")
st.plotly_chart(fig)

# Acurácia por categoria
if "question_type" in df_modelo.columns:
    st.subheader("Acurácia por Tipo de Questão")
    acc_tipo = df_modelo.groupby("question_type")["is_correct"].mean().reset_index()
    acc_tipo["is_correct"] *= 100
    fig = px.bar(acc_tipo, x="question_type", y="is_correct", title="Acurácia (%) por Tipo de Questão")
    st.plotly_chart(fig)

print(df_modelo.columns)
# Quantidade de frames analisados em relacao ao total por video
if "total_frames" in df_modelo.columns and "frames_analyzed" in df_modelo.columns:
    st.subheader("Frames Analisados por Vídeo")
    df_modelo["percentual_frames"] = (df_modelo["frames_analyzed"] / df_modelo["total_frames"]) * 100
    fig = px.histogram(df_modelo, x="percentual_frames", nbins=20, title="Distribuição do Percentual de Frames Analisados")
    st.plotly_chart(fig)