import streamlit as st
import fitz
from rapidfuzz import process

st.set_page_config(
    page_title="Oracle 1Z0-083",
    page_icon="📚"
)

st.title("📚 Oracle 1Z0-083 Study")

pdf_file = "Exam Dump 1Z0-083.pdf"

@st.cache_data
def carregar_pdf():

    doc = fitz.open(pdf_file)

    paginas = []

    for numero, pagina in enumerate(doc):

        texto = pagina.get_text()

        paginas.append({
            "pagina": numero + 1,
            "texto": texto
        })

    return paginas

dados = carregar_pdf()

st.success(
    f"PDF carregado com {len(dados)} páginas."
)

texto_busca = st.text_input(
    "Digite parte da pergunta:"
)

if texto_busca:

    textos = [
        p["texto"]
        for p in dados
    ]

    resultado = process.extractOne(
        texto_busca,
        textos
    )

    texto_encontrado, score, indice = resultado

    st.write(
        f"Similaridade: {score:.2f}%"
    )

    st.subheader(
        f"Página {dados[indice]['pagina']}"
    )

    st.text_area(
        "Conteúdo encontrado",
        texto_encontrado,
        height=400
    )
