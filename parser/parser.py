import pdfplumber
import json
import os
from pathlib import Path


PDF_DIR = os.getenv("PDF_DIR", "../data/pdfs")
TEXT_DIR = os.getenv("TEXT_DIR", "../data/textos")


def extrair_texto(caminho_pdf: str) -> dict:
    nome_arquivo = Path(caminho_pdf).stem
    partes = nome_arquivo.split("_")

    metadata = {
        "arquivo": nome_arquivo,
        "data": partes[1] if len(partes) > 1 else None,
        "caderno": partes[2] if len(partes) > 2 else None,
    }

    paginas = []
    with pdfplumber.open(caminho_pdf) as pdf:
        for i, pagina in enumerate(pdf.pages, start=1):
            texto = pagina.extract_text()
            if texto:
                paginas.append({
                    "pagina": i,
                    "texto": texto.strip()
                })

    metadata["total_paginas"] = len(paginas)
    metadata["paginas"] = paginas

    return metadata


def salvar_json(dados: dict, nome_arquivo: str):
    os.makedirs(TEXT_DIR, exist_ok=True)
    caminho = f"{TEXT_DIR}/{nome_arquivo}.json"
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"[OK] {caminho} ({dados['total_paginas']} páginas)")
    return caminho


def processar_pdfs():
    pdfs = list(Path(PDF_DIR).glob("*.pdf"))
    if not pdfs:
        print("[AVISO] Nenhum PDF encontrado em", PDF_DIR)
        return

    for pdf in pdfs:
        print(f"[PROCESSANDO] {pdf.name}")
        dados = extrair_texto(str(pdf))
        salvar_json(dados, pdf.stem)


if __name__ == "__main__":
    processar_pdfs()
