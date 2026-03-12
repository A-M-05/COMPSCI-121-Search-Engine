from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning, MarkupResemblesLocatorWarning
import warnings
import re

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

_WHITESPACE_RE = re.compile(r"\s+")

def _normalize_whitespaces(text: str) -> str:
    """
    Collapse all consecutive whitespace characters into a single space
    and trim leading and trailing whitespace.

    :param text: Input string to normalize.
    :type text: str
    :return: Whitespace-normalized string.
    :rtype: str
    """
    return _WHITESPACE_RE.sub(" ", text).strip()

def extract_fields(html: str) -> dict[str, str]:
    """
    Extract important textual fields from HTML content for indexing.

    The returned dictionary always contains the following keys:
    "title", "headings", "bold", and "body".
    All returned values are whitespace-normalized strings.

    :param html: Raw HTML content of a document.
    :type html: str
    :return: Dictionary containing extracted text fields.
    :rtype: dict[str, str]
    """
    if not html:
        return {"title": "", "headings": "", "bold": "", "body": ""}

    soup = BeautifulSoup(html, "lxml")

    # Remove non-content nodes
    for tag in soup(["script", "style"]):
        tag.decompose()

    # Title
    title_text = ""
    title_tag = soup.title
    if title_tag:
        title_text = _normalize_whitespaces(title_tag.get_text(separator=" ", strip=True))
        title_tag.decompose()

    # Headings (remove as we extract to avoid double counting in body)
    headings_parts: list[str] = []
    for tag in soup.find_all(["h1", "h2", "h3"]):
        heading = _normalize_whitespaces(tag.get_text(separator=" ", strip=True))
        if heading:
            headings_parts.append(heading)
        tag.decompose()
    headings_text = _normalize_whitespaces(" ".join(headings_parts)) if headings_parts else ""

    # Bold (remove as we extract to avoid double counting in body)
    bold_parts: list[str] = []
    for tag in soup.find_all(["b", "strong"]):
        bold = _normalize_whitespaces(tag.get_text(separator=" ", strip=True))
        if bold:
            bold_parts.append(bold)
        tag.decompose()
    bold_text = _normalize_whitespaces(" ".join(bold_parts)) if bold_parts else ""

    # Remaining visible text
    body_text = _normalize_whitespaces(soup.get_text(separator=" ", strip=True))

    return {
        "title": title_text,
        "headings": headings_text,
        "bold": bold_text,
        "body": body_text,
    }