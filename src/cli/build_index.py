from ..config.settings import (
    DEV_ROOT, DOC_TABLE_PATH, FIELD_WEIGHTS, PARTIAL_PATH, 
    DOC_LENGTHS_PATH, COLLECTION_STATS_PATH, BIGRAM_INDEX_PATH, EXACT_DUPLICATES_PATH,
    NEAR_DUPLICATES_PATH
)
from ..indexing.accumulator import IndexAccumulator
from ..io.dataset_reader import iterate_documents
from ..text.html_extractor import extract_fields
from ..text.tokstem import normalize
from ..extra.duplicate_detector import DuplicateDetector
import math

def build_index():
    """
    Builds inverted index:
        - assigns docIDs
        - extracts + weights tokens (including Anchor Text for Task 4)
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
    duplicate_detector = DuplicateDetector()
    accumulator = IndexAccumulator()

    # TASK 4: Anchor Map
    # Key: normalized_target_url, Value: list of anchor text strings found on other pages
    anchor_map = {}

    # Ensure output directories exist
    DOC_TABLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PARTIAL_PATH.mkdir(parents=True, exist_ok=True)
    DOC_LENGTHS_PATH.parent.mkdir(parents=True, exist_ok=True)
    COLLECTION_STATS_PATH.parent.mkdir(parents=True, exist_ok=True)
    BIGRAM_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXACT_DUPLICATES_PATH.parent.mkdir(parents=True, exist_ok=True)
    NEAR_DUPLICATES_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(DOC_TABLE_PATH, "w") as doc_table, \
         open(DOC_LENGTHS_PATH, "w") as doc_lengths, \
         open(COLLECTION_STATS_PATH, "w") as collection_stats, \
         open(BIGRAM_INDEX_PATH, "w") as bigram_index, \
         open(EXACT_DUPLICATES_PATH, "w") as exact_duplicates, \
         open(NEAR_DUPLICATES_PATH, "w") as near_duplicates:

        # Iterate through dataset documents (url, html)
        for _, url, html in iterate_documents(DEV_ROOT):

            # Skip duplicate URLs
            if url in seen_urls:
                continue
            
            # Receive both fields and the discovered outbound links from HTML
            fields, links = extract_fields(html)

            # ------------ ANCHOR TEXT COLLECTION ------------
            for target_url, anchor_text in links:
                if target_url not in anchor_map:
                    anchor_map[target_url] = []
                anchor_map[target_url].append(anchor_text)
            # --------------------------------------------------------

            # ------------ EXACT DUPLICATE PAGE DETECTION ------------
            is_exact_dup, kept_doc_id, kept_url = duplicate_detector.check_exact(
                url = url,
                fields = fields,
                current_doc_id = new_doc_id
            )

            if is_exact_dup:
                exact_duplicates.write(f"{url}\t{kept_doc_id}\t{kept_url}\n")
                continue
            # --------------------------------------------------------

            # Write to doc_table, mapping is docID -> URL
            doc_table.write(f"{new_doc_id}\t{url}\n")
            seen_urls.add(url)

            # Build postings list for each term in document
            local_counts = dict()
            local_positions = dict()
            position_counter = 0

            # Build weighted term frequencies using standard field weights
            for field_name in ["title", "headings", "bold", "body"]:
                text = fields[field_name]
                tokens = normalize(text)
                weight = FIELD_WEIGHTS.get(field_name, 1.0)

                for token in tokens:
                    local_counts[token] = local_counts.get(token, 0) + weight

                    # Track position for each token
                    if token not in local_positions:
                        local_positions[token] = []
                    local_positions[token].append(position_counter)
                    position_counter += 1

            # ------------ ANCHOR TEXT PROCESSING ------------
            if url in anchor_map:
                anchor_weight = FIELD_WEIGHTS.get("anchor", 2.0)
                for anchor_text in anchor_map[url]:
                    anchor_tokens = normalize(anchor_text)
                    for token in anchor_tokens:
                        local_counts[token] = local_counts.get(token, 0) + anchor_weight
                
                # Free memory: we've applied these anchors, no need to keep them
                del anchor_map[url]
            # --------------------------------------------------------

            # ------------ NEAR DUPLICATE PAGE DETECTION ------------
            near_matches = duplicate_detector.check_near(
                url=url,
                current_doc_id=new_doc_id,
                local_counts=local_counts
            )

            for prior_doc_id, prior_url, distance in near_matches:
                near_duplicates.write(
                    f"{new_doc_id}\t{url}\t{prior_doc_id}\t{prior_url}\t{distance}\n"
                )
            # --------------------------------------------------------

            # Generate bigrams from body text for proximity boosting
            body_tokens = normalize(fields['body'])
            for i in range(len(body_tokens) - 1):
                bigram = body_tokens[i] + '_' + body_tokens[i + 1]
                bigram_index.write(f"{new_doc_id}\t{bigram}\n")

            # Compute document vector length for cosine normalization
            sum_sq = 0
            for weighted_tf in local_counts.values():
                if weighted_tf > 0:
                    # w_td = 1 + log10(tf)
                    w_td = 1 + math.log10(weighted_tf)
                    sum_sq += w_td ** 2

            doc_length = math.sqrt(sum_sq)

            # Write to doc_lengths
            doc_lengths.write(f"{new_doc_id}\t{doc_length}\n")

            # Add document postings into in-memory accumulator
            accumulator.add_document(doc_id=new_doc_id, local_positions=local_positions)
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

        # Write total docs to stats file
        collection_stats.write(f"total_docs\t{doc_count}\n")

    # Summary stats for sanity-checking index build
    print("--------------------------------------------------")
    print("Finished building the inverted index.")
    print(f"\tNumber of documents processed: {doc_count}")
    print(f"\tNumber of partials created:    {partial_num}")
    print(f"\tNumber of postings written:    {total_postings_written}")
    print(f"\tRemaining orphan anchors:      {len(anchor_map)}") 
    print("--------------------------------------------------")

if __name__ == "__main__":
    build_index()