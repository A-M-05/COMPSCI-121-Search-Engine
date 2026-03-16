from urllib.parse import urldefrag, urlsplit, urlunsplit
from pathlib import Path
import json


def list_json_files(directory: str) -> list[Path]:
    """
    Recursively collect all JSON files under a directory.

    This is used as the first step in dataset iteration so the crawler
    processes documents deterministically and consistently across runs.

    :param directory: Root directory containing the dataset.
    :type directory: str
    :return: List of JSON file paths.
    :rtype: list[Path]
    """

    base_path = Path(directory)

    # rglob ensures full recursive traversal across subdirectories.
    json_files = [p for p in base_path.rglob("*.json") if p.is_file()]
    return json_files


def normalize_url(url: str) -> str:
    """
    Normalize a URL into a canonical representation.

    This ensures consistent indexing and prevents duplicates caused by
    formatting variations. The normalization includes:
    - removing fragments
    - lowercasing scheme and hostname
    - removing default ports
    - trimming trailing slashes (except root)

    :param url: Raw URL string.
    :type url: str
    :return: Canonicalized URL or empty string if invalid.
    :rtype: str
    """

    if not url:
        return ""

    # Remove fragment and safely split into components.
    try:
        clean_url, _ = urldefrag(url)
        split = urlsplit(clean_url)
    except Exception:
        return ""

    scheme = (split.scheme or "").lower()
    netloc = (split.netloc or "").lower()
    path = split.path or "/"
    query = split.query

    # Remove default ports to avoid duplicate representations.
    if scheme == "http" and netloc.endswith(":80"):
        netloc = netloc[:-3]
    elif scheme == "https" and netloc.endswith(":443"):
        netloc = netloc[:-4]

    # Normalize trailing slash (but preserve root).
    if path != "/":
        path = path.rstrip("/") or "/"

    return urlunsplit((scheme, netloc, path, query, ""))


def iterate_documents(root_path: str):
    """
    Yield documents from the dataset in deterministic order.

    Each yielded item includes:
        (doc_id, normalized_url, html_content)

    The function:
    - gathers all JSON files
    - sorts them for stable iteration
    - safely loads content
    - normalizes URLs
    - assigns incremental docIDs

    Invalid or malformed files are skipped silently to prevent
    pipeline interruption.

    :param root_path: Root dataset directory.
    :type root_path: str
    :yield: Tuple containing docID, normalized URL, and HTML content.
    :rtype: tuple[int, str, str]
    """

    doc_id = 0
    json_files = list_json_files(root_path)

    # Sorting ensures reproducible indexing results across runs.
    json_files.sort()

    for file_path in json_files:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                data = json.load(file)
        except Exception:
            # Skip unreadable or malformed files.
            continue

        url = data.get("url")
        html_content = data.get("content")

        # Skip documents without URLs since they cannot be indexed.
        if not url:
            continue

        if html_content is None:
            html_content = ""

        normalized_url = normalize_url(url)

        yield (doc_id, normalized_url, html_content)

        doc_id += 1
