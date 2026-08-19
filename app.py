import streamlit as st
import fitz
import re
from rapidfuzz import process, fuzz

st.set_page_config(
    page_title="Oracle 1Z0-083 Study",
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


questoes = carregar_questoes()

st.sidebar.title("Navegação")

numeros_questoes = [
    q["numero"]
    for q in questoes
]

questao_sidebar = st.sidebar.selectbox(
    "Ir para questão",
    numeros_questoes
)

st.success(
    f"{len(questoes)} questões carregadas."
)

modo_busca = st.radio(
    "Tipo de busca",
    ["Texto", "Número da Questão"]
)

valor_busca = st.text_input(
    "Digite sua busca:"
)

if st.sidebar.button("Abrir Questão"):

    for q in questoes:

        if q["numero"] == questao_sidebar:

            st.metric(
                "Similaridade",
                "100%"
            )

            st.subheader(
                f"Questão {q['numero']}"
            )

            linhas = q["conteudo"].split("\n")

            pergunta = []
            alternativas = []

            for linha in linhas:

                linha = linha.strip()

                if re.match(r"^[A-F]\.", linha):
                    alternativas.append(linha)
                else:
                    pergunta.append(linha)

            st.markdown("### Pergunta")
            st.write("\n".join(pergunta))

            st.markdown("### Alternativas")

            for alt in alternativas:
                st.write(alt)

            st.stop()

if valor_busca:

    if modo_busca == "Número da Questão":

        questao = None

        for q in questoes:

            if q["numero"] == valor_busca.strip():

                questao = q
                score = 100
                break

        if questao is None:

            st.error(
                "Questão não encontrada."
            )

            st.stop()

    else:

        textos = [
            q["conteudo"]
            for q in questoes
        ]

        resultado = process.extractOne(
            valor_busca,
            textos,
            scorer=fuzz.token_set_ratio
        )

        texto, score, indice = resultado

        questao = questoes[indice]

    linhas = questao["conteudo"].split("\n")

    pergunta = []
    alternativas = []

    for linha in linhas:

        linha = linha.strip()

        if re.match(r"^[A-F]\.", linha):
            alternativas.append(linha)
        else:
            pergunta.append(linha)

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
