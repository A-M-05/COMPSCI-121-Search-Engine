from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning, MarkupResemblesLocatorWarning
import warnings
import re
# Import the team's normalization logic
from ..io.dataset_reader import normalize_url 

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

_WHITESPACE_RE = re.compile(r"\s+")

def _normalize_whitespaces(text: str) -> str:
    """Collapse all consecutive whitespace characters and trim."""
    return _WHITESPACE_RE.sub(" ", text).strip()

def extract_fields(html: str) -> tuple[dict[str, str], list[tuple[str, str]]]:
    """
    Extract textual fields AND anchor text targeting other pages.
    Returns: (fields_dict, list_of_links)
    """
    if not html:
        return {"title": "", "headings": "", "bold": "", "body": ""}, []

    soup = BeautifulSoup(html, "lxml")

    # ------------ ANCHOR TEXT EXTRACTION ------------
    links = []
    for a_tag in soup.find_all("a", href=True):
        raw_url = a_tag["href"]
        # Normalize target URL to match index keys
        try:
            target_url = normalize_url(raw_url)
        except ValueError:
            continue
        except Exception:
            continue
        anchor_text = _normalize_whitespaces(a_tag.get_text(separator=" ", strip=True))
        
        if anchor_text and target_url:
            links.append((target_url, anchor_text))

    # ------------ FIELD EXTRACTION ------------
    for tag in soup(["script", "style"]):
        tag.decompose()

    # Title
    title_text = ""
    title_tag = soup.title
    if title_tag:
        title_text = _normalize_whitespaces(title_tag.get_text(separator=" ", strip=True))
        title_tag.decompose()

    # Headings
    headings_parts: list[str] = []
    for tag in soup.find_all(["h1", "h2", "h3"]):
        heading = _normalize_whitespaces(tag.get_text(separator=" ", strip=True))
        if heading:
            headings_parts.append(heading)
        tag.decompose()
    headings_text = _normalize_whitespaces(" ".join(headings_parts)) if headings_parts else ""

    # Bold
    bold_parts: list[str] = []
    for tag in soup.find_all(["b", "strong"]):
        bold = _normalize_whitespaces(tag.get_text(separator=" ", strip=True))
        if bold:
            bold_parts.append(bold)
        tag.decompose()
    bold_text = _normalize_whitespaces(" ".join(bold_parts)) if bold_parts else ""

    # Remaining body text
    body_text = _normalize_whitespaces(soup.get_text(separator=" ", strip=True))

    fields = {
        "title": title_text,
        "headings": headings_text,
        "bold": bold_text,
        "body": body_text,
    }

    return fields, links