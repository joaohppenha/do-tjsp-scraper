import requests
import os
from datetime import datetime, timedelta

BASE_URL = "https://www.tjsp.jus.br/atcapi/dje/v1/caderno/download"

CADERNOS = {
    "administrativo": 10,
    "judicial_1": 11,
    "judicial_2": 12,
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
}

OUTPUT_DIR = os.getenv("PDF_DIR", "../data/pdfs")


def baixar_caderno(data: str, id_caderno: int, nome_caderno: str) -> str | None:
    params = {
        "data": data,
        "idCaderno": id_caderno,
        "v2": "true",
        "diarioFuturo": "false",
        "V2": "true",
    }

    response = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=60)

    if response.status_code != 200:
        print(f"[ERRO] {data} | {nome_caderno} | status {response.status_code}")
        return None

    if "application/pdf" not in response.headers.get("Content-Type", ""):
        print(f"[AVISO] {data} | {nome_caderno} | resposta nao e PDF")
        return None

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    nome_arquivo = f"{OUTPUT_DIR}/DJE_{data}_{nome_caderno}.pdf"

    with open(nome_arquivo, "wb") as f:
        f.write(response.content)

    print(f"[OK] {nome_arquivo} ({len(response.content) / 1024 / 1024:.2f} MB)")
    return nome_arquivo


def coletar_ultimos_dias(dias: int = 30):
    hoje = datetime.today()
    for i in range(1, dias + 1):
        data = (hoje - timedelta(days=i)).strftime("%Y-%m-%d")
        for nome, id_caderno in CADERNOS.items():
            baixar_caderno(data, id_caderno, nome)


if __name__ == "__main__":
    coletar_ultimos_dias(dias=30)
