import streamlit as st

st.set_page_config(
    page_title="Oracle 1Z0-083",
    page_icon="📚"
)

st.title("📚 Oracle 1Z0-083 Study")

st.write(
    "Aplicação de busca de questões Oracle 1Z0-083."
)

pergunta = st.text_input(
    "Digite uma pergunta para teste:"
)

if pergunta:
    st.success(
        f"Você digitou: {pergunta}"
    )
