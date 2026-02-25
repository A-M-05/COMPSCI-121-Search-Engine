# src/cli/merge_partials.py

from ..indexing.merger import Merger
from ..config.settings import MERGED_POSTINGS_PATH, DICTIONARY_PATH, DOC_TABLE_PATH


def main() -> None:
    # Run the merge
    Merger().merge_partials()

    # After merge completes, compute on-disk sizes (final index files only)
    postings_size = MERGED_POSTINGS_PATH.stat().st_size if MERGED_POSTINGS_PATH.exists() else 0
    dictionary_size = DICTIONARY_PATH.stat().st_size if DICTIONARY_PATH.exists() else 0
    doc_table_size = DOC_TABLE_PATH.stat().st_size if DOC_TABLE_PATH.exists() else 0

    total_size = postings_size + dictionary_size + doc_table_size

    print(f"Postings size (bytes): {postings_size}")
    print(f"Dictionary size (bytes): {dictionary_size}")
    print(f"Doc table size (bytes): {doc_table_size}")
    print(f"Total index size (bytes): {total_size}")
    print(f"Total index size (KB): {total_size / 1024:.2f}")
    print(f"Total index size (MB): {total_size / (1024 * 1024):.2f}")


if __name__ == "__main__":
    main()