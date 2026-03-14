from urllib.parse import urldefrag, urlsplit, urlunsplit
from pathlib import Path
import json


def list_json_files(directory : str) -> list[Path]:
    """
    Recursively list all file paths in a directory.
    
    :param directory: Path of directory
    :type directory: str
    """

    base_path = Path(directory)
    json_files = [p for p in base_path.rglob('*.json') if p.is_file()]
    return json_files


def normalize_url(url: str) -> str:
    """
    Normalize and create a canonical representation of a URL.
    - Removes fragments.
    - Lowercases scheme and hostname.
    - Removes default ports.
    - Strips trailing slash.
    
    :param url: Non-normalized URL.
    :type url: str
    """

    if not url:
        return ""

    # Remove fragment and split into components
    try:
        clean_url, _ = urldefrag(url)
        split = urlsplit(clean_url)
    except ValueError:
        return ""
    except Exception:
        return ""

    scheme = (split.scheme or "").lower()
    netloc = (split.netloc or "").lower()
    path = split.path or "/"
    query = split.query

    # Remove default ports
    if scheme == "http" and netloc.endswith(":80"):
        netloc = netloc[:-3]
    elif scheme == "https" and netloc.endswith(":443"):
        netloc = netloc[:-4]

    # Normalize path (remove trailing slash unless root)
    if path != "/":
        path = path.rstrip("/") or "/"

    return urlunsplit((scheme, netloc, path, query, ""))


def iterate_documents(root_path : str):
    doc_id = 0
    json_files = list_json_files(root_path)

    json_files.sort()

    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors = 'ignore') as file:
                data = json.load(file)
        except FileNotFoundError:
            continue
        except json.JSONDecodeError as e:
            continue
        except Exception as e:
            continue

        url = data.get('url')
        html_content = data.get('content')

        if not url:
            continue

        if html_content is None:
            html_content = ""

        normalized_url = normalize_url(url)

        yield (doc_id, normalized_url, html_content)

        doc_id += 1
    