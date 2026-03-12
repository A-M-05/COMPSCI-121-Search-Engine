from .build_index import build_index
from .merge_partials import merge
from .search import search

def main() -> None:
    print("=== BUILDING INDEX ===")
    build_index()

    print("\n=== MERGING PARTIALS ===")
    merge()

    print("\n=== STARTING SEARCH ===")
    search()


if __name__ == "__main__":
    main()