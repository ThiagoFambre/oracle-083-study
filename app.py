import streamlit as st
import fitz
import re
import numpy as np
import easyocr

from PIL import Image
from rapidfuzz import process, fuzz


st.set_page_config(
    page_title="Oracle 1Z0-083 Study",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Oracle 1Z0-083 Study")

PDF_FILE = "Exam Dump 1Z0-083.pdf"


@st.cache_data
def carregar_questoes():

    doc = fitz.open(PDF_FILE)

    texto_completo = ""

    for pagina in doc:
        texto_completo += pagina.get_text() + "\n"

    padrao = r"Question\s+(\d+)(.*?)(?=Question\s+\d+|$)"

    resultados = re.findall(
        padrao,
        texto_completo,
        flags=re.S | re.I
    )

    questoes = []

    for numero, conteudo in resultados:

        questoes.append({
            "numero": numero,
            "conteudo": conteudo.strip()
        })

    return questoes


@st.cache_resource
def carregar_ocr():

    return easyocr.Reader(
        ["en"],
        gpu=False
    )


def separar_pergunta_alternativas(conteudo):

    linhas = conteudo.split("\n")

    pergunta = []
    alternativas = []

    for linha in linhas:

        linha = linha.strip()

        if not linha:
            continue

        if re.match(r"^[A-F]\.", linha):
            alternativas.append(linha)
        else:
            pergunta.append(linha)

    return pergunta, alternativas


def mostrar_questao(questao, score):

    pergunta, alternativas = separar_pergunta_alternativas(
        questao["conteudo"]
    )

    st.metric(
        "Similaridade",
        f"{score:.2f}%"
    )

    st.subheader(
        f"Questão {questao['numero']}"
    )

    st.markdown("### Pergunta")

    st.write(
        "\n".join(pergunta)
    )

    st.markdown("### Alternativas")

    for alt in alternativas:
        st.write(alt)


def buscar_questao_por_texto(texto_busca, questoes):

    textos = [
        q["conteudo"]
        for q in questoes
    ]

    resultado = process.extractOne(
        texto_busca,
        textos,
        scorer=fuzz.token_set_ratio
    )

    texto, score, indice = resultado

    return questoes[indice], score


def buscar_questao_por_numero(numero, questoes):

    for q in questoes:

        if q["numero"] == numero.strip():

            return q

    return None


questoes = carregar_questoes()

st.success(
    f"{len(questoes)} questões carregadas."
)

st.caption(
    "Você pode pesquisar por texto, número da questão ou usar a câmera do celular."
)


# -------------------------------
# Navegação lateral
# -------------------------------

st.sidebar.title("Navegação")

numeros_questoes = [
    q["numero"]
    for q in questoes
]

questao_sidebar = st.sidebar.selectbox(
    "Ir para questão",
    numeros_questoes
)

if st.sidebar.button("Abrir Questão"):

    questao = buscar_questao_por_numero(
        questao_sidebar,
        questoes
    )

    if questao:
        mostrar_questao(
            questao,
            100
        )

    st.stop()


# -------------------------------
# Busca manual
# -------------------------------

st.markdown("## Busca manual")

modo_busca = st.radio(
    "Tipo de busca",
    ["Texto", "Número da Questão"]
)

valor_busca = st.text_input(
    "Digite sua busca:"
)

if valor_busca:

    if modo_busca == "Número da Questão":

        questao = buscar_questao_por_numero(
            valor_busca,
            questoes
        )

        if questao is None:

            st.error(
                "Questão não encontrada."
            )

        else:

            mostrar_questao(
                questao,
                100
            )

    else:

        questao, score = buscar_questao_por_texto(
            valor_busca,
            questoes
        )

        mostrar_questao(
            questao,
            score
        )


# -------------------------------
# Busca pela câmera
# -------------------------------

st.divider()

st.markdown("## Buscar usando câmera do celular")

st.info(
    "Aponte a câmera para a questão e tire uma foto. O sistema fará OCR da imagem e tentará localizar a questão correspondente no PDF."
)

foto = st.camera_input(
    "Fotografe a questão"
)

if foto:

    imagem = Image.open(foto).convert("RGB")

    st.image(
        imagem,
        caption="Imagem capturada",
        use_container_width=True
    )

    reader = carregar_ocr()

    with st.spinner("Lendo texto da imagem..."):

        resultado_ocr = reader.readtext(
            np.array(imagem),
            detail=0,
            paragraph=True
        )

    texto_extraido = " ".join(resultado_ocr).strip()

    st.markdown("### Texto identificado pela câmera")

    st.text_area(
        "OCR",
        texto_extraido,
        height=180
    )

    if texto_extraido:

        questao, score = buscar_questao_por_texto(
            texto_extraido,
            questoes
        )

        st.markdown("## Resultado encontrado")

        if score < 45:

            st.warning(
                "A similaridade ficou baixa. Se a questão encontrada não estiver correta, tire outra foto mais nítida e centralizada."
            )

        mostrar_questao(
            questao,
            score
        )

    else:

        st.warning(
            "Não foi possível identificar texto na imagem. Tire outra foto com melhor iluminação."
        )
