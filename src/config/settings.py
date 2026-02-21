from pathlib import Path

DEV_ROOT = Path("DEV")

OUTPUT_DIR = Path("src/output/")

DOC_TABLE_PATH = OUTPUT_DIR / "doc_table.tsv"

PARTIAL_PATH = Path("src/output/partial/")

ACCUMULATOR_THRESHOLD = 500_000

MERGED_POSTINGS_PATH = OUTPUT_DIR / "merged" / "postings.tsv"

DICTIONARY_PATH = OUTPUT_DIR / "merged" / "dictionary.tsv"

FIELD_WEIGHTS = {
    "title" : 3.0,
    "headings" : 2.0,
    "bold" : 1.5,
    "body" : 1.0
}