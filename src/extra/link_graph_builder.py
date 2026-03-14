from ..config.settings import DOC_TABLE_PATH, GRAPH_EDGES_PATH, DEV_ROOT
from ..io.dataset_reader import iterate_documents
from ..text.html_extractor import extract_fields

def load_doc_table():
    url_to_doc_id = {}

    if not DOC_TABLE_PATH.exists():
        raise FileNotFoundError
    
    with open(DOC_TABLE_PATH, "r") as doc_table:
        for line in doc_table:
            line = line.strip()
            if not line:
                continue
            l = line.split('\t', 1)
            doc_id, url = int(l[0]), l[1]
            url_to_doc_id[url] = doc_id
    return url_to_doc_id


def build_graph():
    url_to_doc_id = load_doc_table()
    seen_edges = set()

    GRAPH_EDGES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(GRAPH_EDGES_PATH, "w") as graph_edges:
        for _, source_url, html in iterate_documents(DEV_ROOT):
            if source_url not in url_to_doc_id:
                continue

            source_doc_id = url_to_doc_id[source_url]

            _, links = extract_fields(html)

            for target_url, _ in links:
                if target_url in url_to_doc_id:
                    target_doc_id = url_to_doc_id[target_url]

                    if target_doc_id != source_doc_id:
                        edge = (source_doc_id, target_doc_id)
                        if edge in seen_edges:
                            continue
                        else:
                            seen_edges.add(edge)
                            graph_edges.write(f"{source_doc_id}\t{target_doc_id}\n")

if __name__ == "__main__":
    build_graph()