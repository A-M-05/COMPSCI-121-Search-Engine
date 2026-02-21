from ..config.settings import DEV_ROOT, DOC_TABLE_PATH, FIELD_WEIGHTS, PARTIAL_PATH
from ..indexing.accumulator import IndexAccumulator
from ..io.dataset_reader import iterate_documents
from ..text.html_extractor import extract_fields
from ..text.tokstem import normalize

def build_index():
    seen_urls = set()
    doc_count = 0
    new_doc_id = 0
    partial_num = 0
    total_postings_written = 0
    total_tokens = set()
    accumulator = IndexAccumulator()

    DOC_TABLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PARTIAL_PATH.mkdir(parents=True, exist_ok=True)

    with open(DOC_TABLE_PATH, "w") as doc_table:
        for doc_id, url, html in iterate_documents(DEV_ROOT):

            if url in seen_urls:
                continue

            # Write to doc_table.
            doc_table.write(f"{new_doc_id}\t{url}\n")

            seen_urls.add(url)

            # Extract fields from HTML.
            fields = extract_fields(html)

            local_counts = dict()

            for field_name in ["title", "headings", "bold", "body"]:
                text = fields[field_name]
                tokens = normalize(text)
                weight = FIELD_WEIGHTS[field_name]

                for token in tokens:
                    total_tokens.add(token)
                    if token in local_counts:
                        local_counts[token] += weight
                    else:
                        local_counts[token] = weight

            accumulator.add_document(doc_id = new_doc_id, local_counts = local_counts)
            doc_count += 1
            new_doc_id += 1

            if accumulator.should_flush():
                total_postings_written += accumulator.postings_count
                accumulator.flush(PARTIAL_PATH / f"partial_{partial_num}.tsv")
                partial_num += 1
        
        if not accumulator.is_empty():
            total_postings_written += accumulator.postings_count
            accumulator.flush(PARTIAL_PATH / f"partial_{partial_num}.tsv")
            partial_num += 1

    print(f"Number of documents processed: {doc_count}")
    print(f"Number of partials created: {partial_num}")
    print(f"Number of postings: {total_postings_written}")
    print(f"Number of tokens: {len(total_tokens)}")

if __name__ == "__main__":
    build_index()