import streamlit as st
import fitz
import re
from rapidfuzz import process, fuzz

st.set_page_config(
    page_title="Oracle 1Z0-083",
    page_icon="📚"
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

    encontrados = re.findall(
        padrao,
        texto_completo,
        flags=re.S | re.I
    )

    questoes = []

    for numero, conteudo in encontrados:

        questoes.append(
            {
                "numero": numero,
                "conteudo": conteudo.strip()
            }
        )

    return questoes


questoes = carregar_questoes()

st.success(
    f"{len(questoes)} questões carregadas."
)

texto_busca = st.text_input(
    "Digite parte da pergunta:"
)

if texto_busca:

    lista_textos = [
        q["conteudo"]
        for q in questoes
    ]

    melhor = process.extractOne(
        texto_busca,
        lista_textos,
        scorer=fuzz.token_set_ratio
    )

    texto, score, indice = melhor

    questao = questoes[indice]

    st.write(
        f"Similaridade: {score:.2f}%"
    )

    st.subheader(
        f"Questão {questao['numero']}"
    )

    st.text_area(
        "Questão encontrada",
        questao["conteudo"],
        height=500
    )
