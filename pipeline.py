import subprocess
import sys
from datetime import datetime, timedelta

def rodar(comando: list, descricao: str):
    print(f"\n[PIPELINE] {descricao}...")
    resultado = subprocess.run(comando, cwd=None)
    if resultado.returncode != 0:
        print(f"[ERRO] Falha em: {descricao}")
        sys.exit(1)
    print(f"[OK] {descricao} concluído")

def main(dias: int = 7):
    print(f"[PIPELINE] Iniciando coleta dos últimos {dias} dias — {datetime.today().strftime('%Y-%m-%d %H:%M')}")

    rodar(
        ["python3", "coletor/coletor.py"],
        f"Coleta dos últimos {dias} dias"
    )

    rodar(
        ["python3", "parser/parser.py"],
        "Parsing dos PDFs"
    )

    rodar(
        ["python3", "indexador/indexador.py"],
        "Indexação no OpenSearch"
    )

    print("\n[PIPELINE] Concluído com sucesso!")

if __name__ == "__main__":
    dias = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    main(dias)
