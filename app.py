import streamlit as st
import fitz
import re
import numpy as np
import easyocr

from PIL import Image
from rapidfuzz import process, fuzz


# -------------------------------
# Configuração da página
# -------------------------------

st.set_page_config(
    page_title="Oracle 1Z0-083 Study",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("📚 Oracle 1Z0-083 Study")

PDF_FILE = "Exam Dump 1Z0-083.pdf"


# -------------------------------
# Funções auxiliares
# -------------------------------

def normalizar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r"\s+", " ", texto)
    texto = texto.replace("_", " ")
    texto = texto.strip()
    return texto


def cor_eh_verde(cor):
    if not cor:
        return False

    try:
        r, g, b = cor[0], cor[1], cor[2]

        if g > 0.45 and r < 0.45 and b < 0.45:
            return True

    except Exception:
        return False

    return False


def extrair_textos_destacados_verde(doc):
    textos_verdes = []

    for pagina in doc:

        retangulos_verdes = []

        desenhos = pagina.get_drawings()

        for desenho in desenhos:

            cor_preenchimento = desenho.get("fill")

            if cor_eh_verde(cor_preenchimento):

                try:
                    retangulos_verdes.append(
                        fitz.Rect(desenho["rect"])
                    )
                except Exception:
                    pass

        if not retangulos_verdes:
            continue

        dados = pagina.get_text("dict")

        for bloco in dados.get("blocks", []):

            for linha in bloco.get("lines", []):

                texto_linha = ""

                for span in linha.get("spans", []):
                    texto_linha += span.get("text", "")

                texto_linha = texto_linha.strip()

                if not texto_linha:
                    continue

                try:
                    bbox_linha = fitz.Rect(linha["bbox"])
                except Exception:
                    continue

                for ret_verde in retangulos_verdes:

                    if bbox_linha.intersects(ret_verde):

                        textos_verdes.append(texto_linha)
                        break

    return textos_verdes


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


def identificar_respostas_corretas(alternativas, textos_verdes):

    respostas = []

    for alternativa in alternativas:

        match_alt = re.match(r"^([A-F])\.\s*(.*)", alternativa)

        if not match_alt:
            continue

        letra = match_alt.group(1)
        texto_alt = match_alt.group(2)

        texto_alt_norm = normalizar_texto(texto_alt)

        for texto_verde in textos_verdes:

            texto_verde_norm = normalizar_texto(texto_verde)

            if not texto_verde_norm:
                continue

            score_1 = fuzz.partial_ratio(
                texto_verde_norm,
                texto_alt_norm
            )

            score_2 = fuzz.token_set_ratio(
                texto_verde_norm,
                texto_alt_norm
            )

            melhor_score = max(score_1, score_2)

            if melhor_score >= 75:

                if letra not in respostas:
                    respostas.append(letra)

    return respostas


@st.cache_data
def carregar_questoes():

    doc = fitz.open(PDF_FILE)

    texto_completo = ""

    for pagina in doc:
        texto_completo += pagina.get_text() + "\n"

    textos_verdes = extrair_textos_destacados_verde(doc)

    padrao = r"Question\s+(\d+)(.*?)(?=Question\s+\d+|$)"

    resultados = re.findall(
        padrao,
        texto_completo,
        flags=re.S | re.I
    )

    questoes = []

    for numero, conteudo in resultados:

        conteudo = conteudo.strip()

        pergunta, alternativas = separar_pergunta_alternativas(conteudo)

        respostas = identificar_respostas_corretas(
            alternativas,
            textos_verdes
        )

        questoes.append({
            "numero": numero,
            "conteudo": conteudo,
            "respostas": respostas
        })

    return questoes


@st.cache_resource
def carregar_ocr():

    return easyocr.Reader(
        ["en", "pt"],
        gpu=False
    )


def mostrar_questao(questao, score):

    pergunta, alternativas = separar_pergunta_alternativas(
        questao["conteudo"]
    )

    respostas = questao.get("respostas", [])

    st.metric(
        "Similaridade",
        f"{score:.2f}%"
    )

    st.subheader(
        f"Questão {questao['numero']}"
    )

    if respostas:

        st.markdown("### ✅ Resposta correta")

        respostas_formatadas = ", ".join(respostas)

        st.success(
            f"Alternativa(s): {respostas_formatadas}"
        )

    else:

        st.warning(
            "Não consegui identificar automaticamente a resposta correta pelo destaque verde desta questão."
        )

    st.markdown("### Pergunta")

    st.write(
        "\n".join(pergunta)
    )

    st.markdown("### Alternativas")

    for alt in alternativas:

        match_alt = re.match(r"^([A-F])\.", alt)

        if match_alt and match_alt.group(1) in respostas:
            st.success(f"✅ {alt}")
        else:
            st.write(alt)


def buscar_questao_por_texto(texto_busca, questoes):

    textos = [
        q["conteudo"]
        for q in questoes
    ]

    resultado = process.extractOne(
        texto_busca,
        textos,
        scorer=fuzz.partial_ratio
    )

    texto, score, indice = resultado

    return questoes[indice], score


def buscar_questao_por_numero(numero, questoes):

    for q in questoes:

        if q["numero"] == numero.strip():

            return q

    return None


# -------------------------------
# Estado da câmera
# -------------------------------

if "camera_key" not in st.session_state:
    st.session_state.camera_key = 0


def voltar_inicio():
    st.session_state.camera_key += 1
    st.rerun()


# -------------------------------
# Carregamento das questões
# -------------------------------

questoes = carregar_questoes()

st.success(
    f"{len(questoes)} questões carregadas."
)

st.caption(
    "Você pode pesquisar por texto, número da questão ou usar a câmera do celular."
)

if st.button("🔄 Voltar ao início / tirar outra foto"):
    voltar_inicio()


# -------------------------------
# Navegação lateral
# -------------------------------

with st.sidebar:

    st.title("Navegação")

    numeros_questoes = [
        q["numero"]
        for q in questoes
    ]

    questao_sidebar = st.selectbox(
        "Ir para questão",
        numeros_questoes
    )

    if st.button("Abrir Questão"):

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

st.markdown("""
### 📷 Captura da questão

Dicas:
- Tire a foto na horizontal.
- Enquadre apenas a questão.
- Evite pegar barras do navegador.
- Procure preencher toda a tela.
- Se a leitura ficar ruim, aproxime mais a câmera.
""")

foto = st.camera_input(
    "Fotografe a questão",
    key=f"camera_{st.session_state.camera_key}"
)

if foto:

    imagem = Image.open(foto).convert("RGB")

    largura, altura = imagem.size

    imagem = imagem.crop(
        (
            int(largura * 0.02),
            int(altura * 0.15),
            int(largura * 0.98),
            int(altura * 0.85)
        )
    )

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
            paragraph=False
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

        st.divider()

        if st.button("📷 Tirar outra foto"):
            voltar_inicio()

    else:

        st.warning(
            "Não foi possível identificar texto na imagem. Tire outra foto com melhor iluminação."
        )

        if st.button("📷 Tentar novamente"):
            voltar_inicio()
