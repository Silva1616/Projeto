import streamlit as st
import pdfplumber


st.set_page_config(
    page_title="Text Normalizer",
    page_icon="📄",
    layout="wide"
)

st.title("Text Normalizer - Pipeline de Pré processamento")
st.markdown("---")

def extarir_pdf(ficheiro) -> str:

    with pdfplumber.open(ficheiro) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()

    return texto


st.header(" Carrega o docuemnto")

ficheiro = st.file_uploader(
    label="Escolhe um ficheiro",
    type=["pdf", "docx", "txt"],
    help="Formatos suportados: PDF, DOCX, TXT"
)