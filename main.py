import streamlit as st
import pdfplumber
import docx
import re
import io
from langdetect import detect, LangDetectException


#  Configuração da página com o streamlit

st.set_page_config(
    page_title="Text Normalizer",
    page_icon="",
    layout="wide"
)

st.title(" Text Normalizer — Pipeline de Pré-Processamento")
st.markdown("---")


# Extração do texto

def extrair_pdf(ficheiro) -> str:

    texto = ""
    with pdfplumber.open(ficheiro) as pdf:
        for numero_pagina, pagina in enumerate(pdf.pages, start=1):
            texto_pagina = pagina.extract_text()
            if texto_pagina:
                texto += f"\n\n--- Página {numero_pagina} ---\n\n"
                texto += texto_pagina
    return texto


def extrair_docx(ficheiro) -> str:

    documento = docx.Document(ficheiro)
    linhas = []
    for paragrafo in documento.paragraphs:
        linhas.append(paragrafo.text)
    return "\n".join(linhas)


def extrair_txt(ficheiro) -> str:

    conteudo_bytes = ficheiro.read()
    encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
    for enc in encodings:
        try:
            return conteudo_bytes.decode(enc)
        except UnicodeDecodeError:
            continue
    # último recurso: substitui caracteres ilegíveis
    return conteudo_bytes.decode("utf-8", errors="replace")


def extrair_texto(ficheiro_carregado) -> tuple:

    nome = ficheiro_carregado.name
    extensao = nome.split(".")[-1].lower()
    try:
        if extensao == "pdf":
            texto = extrair_pdf(ficheiro_carregado)
        elif extensao == "docx":
            texto = extrair_docx(ficheiro_carregado)
        elif extensao == "txt":
            texto = extrair_txt(ficheiro_carregado)
        else:
            return "", f"Formato '.{extensao}' não suportado."
        return texto, ""
    except Exception as e:
        return "", f"Erro ao processar o ficheiro: {str(e)}"


# Pipeline de limpeza

def remover_artefactos(texto: str) -> str:

    # Remove caracteres de controlo (exceto \n e \t)
    texto = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', texto)
    # Remove caracteres Unicode inválidos (replacement character)
    texto = texto.replace('\ufffd', '')
    # Remove símbolos gráficos e blocos Unicode raros
    texto = re.sub(r'[\u2580-\u259f\u25a0-\u25ff]', '', texto)
    return texto


def remover_cabecalhos_rodapes(texto: str) -> str:

    linhas = texto.splitlines()
    # Conta quantas vezes cada linha aparece (ignora linhas vazias)
    contagem = {}
    for linha in linhas:
        linha_limpa = linha.strip()
        if linha_limpa:
            contagem[linha_limpa] = contagem.get(linha_limpa, 0) + 1

    # Remove linhas que aparecem 3 ou mais vezes
    linhas_filtradas = []
    for linha in linhas:
        if contagem.get(linha.strip(), 0) < 3:
            linhas_filtradas.append(linha)

    return "\n".join(linhas_filtradas)


def reconstruir_paragrafos(texto: str) -> str:

    # Normaliza \r\n para \n
    texto = texto.replace('\r\n', '\n').replace('\r', '\n')
    # Junta linhas que foram partidas a meio de uma frase
    texto = re.sub(r'(?<![.!?:])\n(?!\n)', ' ', texto)
    return texto


def normalizar_espacos(texto: str) -> str:

    # Substitui tabs por espaço
    texto = texto.replace('\t', ' ')
    # Remove espaços múltiplos (mantém um só)
    texto = re.sub(r' {2,}', ' ', texto)
    # Remove espaço antes de pontuação
    texto = re.sub(r' ([.,;:!?])', r'\1', texto)
    # Remove espaços no início e fim de cada linha
    linhas = [linha.strip() for linha in texto.splitlines()]
    texto = "\n".join(linhas)
    # Reduz mais de 2 linhas vazias seguidas para apenas 2
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    return texto


def normalizar_pontuacao(texto: str) -> str:

    # Aspas curvas para aspas retas
    texto = texto.replace('\u201c', '"').replace('\u201d', '"')
    texto = texto.replace('\u2018', "'").replace('\u2019', "'")
    # Travessão longo para hífen duplo
    texto = texto.replace('\u2014', '--').replace('\u2013', '-')
    # Reticências em caractere único para três pontos
    texto = texto.replace('\u2026', '...')
    return texto


def remover_separadores_pagina(texto: str) -> str:

    texto = re.sub(r'\n?--- Página \d+ ---\n?', '\n\n', texto)
    return texto


def aplicar_pipeline(texto: str, opcoes: dict) -> str:

    if opcoes.get("remover_separadores"):
        texto = remover_separadores_pagina(texto)

    if opcoes.get("remover_artefactos"):
        texto = remover_artefactos(texto)

    if opcoes.get("remover_cabecalhos"):
        texto = remover_cabecalhos_rodapes(texto)

    if opcoes.get("reconstruir_paragrafos"):
        texto = reconstruir_paragrafos(texto)

    if opcoes.get("normalizar_pontuacao"):
        texto = normalizar_pontuacao(texto)

    if opcoes.get("normalizar_espacos"):
        texto = normalizar_espacos(texto)

    return texto.strip()



# Para correr o código: python -m streamlit run main.py
#
#dependências:
#streamlit
#pdfplumber
#python-docx
