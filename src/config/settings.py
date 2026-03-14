from pathlib import Path

DEV_ROOT = Path("DEV")

OUTPUT_DIR = Path("src/output/")

DOC_TABLE_PATH = OUTPUT_DIR / "doc_table.tsv"

PARTIAL_PATH = Path("src/output/partial/")

ACCUMULATOR_THRESHOLD = 500_000

MERGED_POSTINGS_PATH = OUTPUT_DIR / "merged" / "postings.tsv"

DICTIONARY_PATH = OUTPUT_DIR / "merged" / "dictionary.tsv"

DOC_LENGTHS_PATH = OUTPUT_DIR / "merged" / "doc_lengths.tsv"

COLLECTION_STATS_PATH = OUTPUT_DIR / "merged" / "collection_stats.tsv"

EXACT_DUPLICATES_PATH = OUTPUT_DIR / "extras" / "exact_duplicates.tsv"

NEAR_DUPLICATES_PATH = OUTPUT_DIR / "extras" / "near_duplicates.tsv"

GRAPH_EDGES_PATH = OUTPUT_DIR / "extras" / "graph_edges.tsv"

PAGERANK_PATH = OUTPUT_DIR / "extras" / "pagerank.tsv"

PAGERANK_ALPHA = 0.85

PAGERANK_ITERATIONS = 20

PAGERANK_SCORE_WEIGHT = 0.2

SIMHASH_BITS = 64

SIMHASH_HAMMING_THRESHOLD = 3

SIMHASH_BUCKET_BITS = 12

BIGRAM_INDEX_PATH = OUTPUT_DIR / "merged" / "bigram_index.tsv"

FIELD_WEIGHTS = {
    "title" : 3.0,
    "headings" : 2.0,
    "bold" : 1.5,
    "body" : 1.0
}

BETA = 0.05
