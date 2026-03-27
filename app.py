import streamlit as st
from opensearchpy import OpenSearch

client = OpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    use_ssl=False,
)

st.set_page_config(page_title="DJE-TJSP", page_icon="⚖️", layout="wide")
st.title("⚖️ Buscador do Diário Eletrônico da Justiça — TJSP")

col1, col2 = st.columns([3, 1])
with col1:
    query = st.text_input("Buscar publicações", placeholder="Ex: resolução, portaria, nome de magistrado...")
with col2:
    tamanho = st.selectbox("Resultados por página", [5, 10, 20], index=1)

data_min, data_max = st.columns(2)
with data_min:
    de = st.date_input("Data inicial")
with data_max:
    ate = st.date_input("Data final")

if query:
    filtros = [{"range": {"data": {"gte": str(de), "lte": str(ate)}}}]

    body = {
        "query": {
            "bool": {
                "must": [{"match": {"texto": {"query": query, "operator": "and"}}}],
                "filter": filtros
            }
        },
        "highlight": {
            "fields": {"texto": {"fragment_size": 300, "number_of_fragments": 2}},
            "pre_tags": ["**"],
            "post_tags": ["**"]
        },
        "_source": ["data", "caderno", "pagina", "arquivo"],
        "size": tamanho
    }

    resp = client.search(index="dje-tjsp", body=body)
    total = resp["hits"]["total"]["value"]
    hits = resp["hits"]["hits"]

    st.markdown(f"**{total} resultado(s) encontrado(s)**")
    st.divider()

    for hit in hits:
        src = hit["_source"]
        trechos = hit.get("highlight", {}).get("texto", [])

        with st.container():
            st.markdown(f"📄 **{src['arquivo']}** · Página {src['pagina']} · {src['data']}")
            for trecho in trechos:
                st.markdown(f"> {trecho}")
            st.divider()
else:
    st.info("Digite um termo acima para buscar publicações do DJE-TJSP.")

    total = client.count(index="dje-tjsp")["count"]
    st.metric("Total de páginas indexadas", total)
