from ..config.settings import DEV_ROOT, DOC_TABLE_PATH, FIELD_WEIGHTS, PARTIAL_PATH, DOC_LENGTHS_PATH, COLLECTION_STATS_PATH
from ..indexing.accumulator import IndexAccumulator
from ..io.dataset_reader import iterate_documents
from ..text.html_extractor import extract_fields
from ..text.tokstem import normalize
import math

def build_index():
    """
    Builds inverted index:
        - assigns docIDs
        - extracts + weights tokens
        - computes doc lengths (for cosine normalization)
        - writes partial indexes for merging
        - records collection stats
    """

    # Setup counters and accumulator
    seen_urls = set()
    doc_count = 0
    new_doc_id = 0
    partial_num = 0
    total_postings_written = 0
    accumulator = IndexAccumulator()

    # Ensure output directories exist
    DOC_TABLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PARTIAL_PATH.mkdir(parents=True, exist_ok=True)
    DOC_LENGTHS_PATH.parent.mkdir(parents=True, exist_ok=True)
    COLLECTION_STATS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(DOC_TABLE_PATH, "w") as doc_table, open(DOC_LENGTHS_PATH, "w") as doc_lengths, open(COLLECTION_STATS_PATH, "w") as collection_stats:
        # Iterate through dataset documents (url, html)
        for _, url, html in iterate_documents(DEV_ROOT):

            # Skip duplicate URLs
            if url in seen_urls:
                continue

            # Write to doc_table, mapping is docID -> URL
            doc_table.write(f"{new_doc_id}\t{url}\n")

            seen_urls.add(url)

            # Extract important fields from HTML (title, headings, bold, body)
            fields = extract_fields(html)

            # Build postings list for each term in document
            local_counts = dict()

            # Build weighted term frequencies using field weights
            for field_name in ["title", "headings", "bold", "body"]:
                # Accumulate weighted term frequencies for this document
                text = fields[field_name]
                tokens = normalize(text)
                weight = FIELD_WEIGHTS[field_name]

                for token in tokens:
                    if token in local_counts:
                        local_counts[token] += weight
                    else:
                        local_counts[token] = weight

            # Compute document vector length 
            # sqrt(sum((1 + log10(weighted_tf))^2))
            # Used later for cosine normalization in ranking
            sum_sq = 0
            for weighted_tf in local_counts.values():
                if weighted_tf > 0:
                    w_td = 1 + math.log10(weighted_tf)
                else:
                    w_td = 0
                
                sum_sq += w_td ** 2

            doc_length = math.sqrt(sum_sq)

            # Write to doc_lengths, used for ranking normalization later
            doc_lengths.write(f"{new_doc_id}\t{doc_length}\n")

            # Add document postings into in-memory accumulator
            accumulator.add_document(doc_id = new_doc_id, local_counts = local_counts)
            doc_count += 1
            new_doc_id += 1

            # Flush to disk when memory threshold reached
            if accumulator.should_flush():
                total_postings_written += accumulator.postings_count
                accumulator.flush(PARTIAL_PATH / f"partial_{partial_num}.tsv")
                partial_num += 1
        
        # Flush remaining postings after processing all documents
        if not accumulator.is_empty():
            total_postings_written += accumulator.postings_count
            accumulator.flush(PARTIAL_PATH / f"partial_{partial_num}.tsv")
            partial_num += 1

        # Write to collection_stats, for IDF during retrieval
        collection_stats.write(f"total_docs\t{doc_count}\n")

    # Summary stats for sanity-checking index build
    print("Finished building the inverted index.")
    print(f"\tNumber of documents processed: {doc_count}")
    print(f"\tNumber of partials created: {partial_num}")
    print(f"\tNumber of postings: {total_postings_written}")
