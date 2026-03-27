import json
import os
from pathlib import Path
from opensearchpy import OpenSearch

TEXT_DIR = os.getenv("TEXT_DIR", "../data/textos")
OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "localhost")
OPENSEARCH_PORT = int(os.getenv("OPENSEARCH_PORT", "9200"))
INDEX_NAME = "dje-tjsp"

client = OpenSearch(
    hosts=[{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}],
    use_ssl=False,
)

MAPPING = {
    "settings": {
        "analysis": {
            "analyzer": {
                "portugues": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "portuguese_stop", "portuguese_stemmer"]
                }
            },
            "filter": {
                "portuguese_stop": {
                    "type": "stop",
                    "stopwords": "_portuguese_"
                },
                "portuguese_stemmer": {
                    "type": "stemmer",
                    "language": "portuguese"
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "arquivo":       {"type": "keyword"},
            "data":          {"type": "date", "format": "yyyy-MM-dd"},
            "caderno":       {"type": "keyword"},
            "pagina":        {"type": "integer"},
            "texto":         {"type": "text", "analyzer": "portugues"},
        }
    }
}


def criar_indice():
    if not client.indices.exists(index=INDEX_NAME):
        client.indices.create(index=INDEX_NAME, body=MAPPING)
        print(f"[OK] Índice '{INDEX_NAME}' criado")
    else:
        print(f"[INFO] Índice '{INDEX_NAME}' já existe")


def indexar_arquivo(caminho_json: str):
    with open(caminho_json, "r", encoding="utf-8") as f:
        dados = json.load(f)

    for pagina in dados["paginas"]:
        doc = {
            "arquivo": dados["arquivo"],
            "data":    dados["data"],
            "caderno": dados["caderno"],
            "pagina":  pagina["pagina"],
            "texto":   pagina["texto"],
        }
        doc_id = f"{dados['arquivo']}_p{pagina['pagina']}"
        client.index(index=INDEX_NAME, id=doc_id, body=doc)

    print(f"[OK] {dados['arquivo']} — {len(dados['paginas'])} páginas indexadas")


def indexar_todos():
    arquivos = list(Path(TEXT_DIR).glob("*.json"))
    if not arquivos:
        print("[AVISO] Nenhum JSON encontrado em", TEXT_DIR)
        return

    criar_indice()
    for arquivo in arquivos:
        print(f"[INDEXANDO] {arquivo.name}")
        indexar_arquivo(str(arquivo))


if __name__ == "__main__":
    indexar_todos()
