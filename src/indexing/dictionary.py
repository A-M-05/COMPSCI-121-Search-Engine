from ..config.settings import DICTIONARY_PATH


class DictionaryWrite:
    def __init__(self):
        # Ensure directory exists
        DICTIONARY_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Open once in write mode (overwrite previous dictionary)
        self.file = open(DICTIONARY_PATH, "w")

    def write_entry(self, term: str, doc_count: int, offset: int) -> None:
        """
        Writes the format: term document_count offset
        into the dictionary file.

        :param term: Word/term stored within the documents
        :type term: str
        :param doc_count: Number of documents containing the word
        :type doc_count: int
        :param offset: Beginning byte offset of term's postings
        :type offset: int
        """
        line = f"{term} {doc_count} {offset}\n"
        self.file.write(line)

    def close(self) -> None:
        """Closes the dictionary file."""
        self.file.close()