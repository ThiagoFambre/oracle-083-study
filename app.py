import streamlit as st
import fitz

st.set_page_config(
    page_title="Oracle 1Z0-083",
    page_icon="📚"
)

st.title("📚 Oracle 1Z0-083 Study")

pdf_file = "Exam Dump 1Z0-083.pdf"

try:

    documento = fitz.open(pdf_file)

    quantidade_paginas = len(documento)

    st.success(
        f"PDF carregado com sucesso!"
    )

    st.write(
        f"Total de páginas: {quantidade_paginas}"
    )

except Exception as erro:

    st.error(
        f"Erro ao abrir PDF: {erro}"
    )
