from pathlib import Path
from ..config.settings import DICTIONARY_PATH
class DictionaryReader:
    def __init__(self):
        self._dict = {}
        self._load()

    def _load(self):
        if not DICTIONARY_PATH.exists():
            raise FileNotFoundError(f'Dictionary not found at {DICTIONARY_PATH}')
    
        with open(DICTIONARY_PATH, 'r', encoding = 'utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(' ')
                if len(parts) != 3:
                    continue
                term, doc_freq, byte_offset = parts
                # byte offset = how many bytes from the start of the file
                # Can go straight to the byte offset ot read whatever needs to be read
                # instead of scanning the whole file
                # Use seek() to do this ^
                self._dict[term] = (int(doc_freq), int(byte_offset))

    def lookup(self, term):
        return self._dict.get(term, None)
    
    def __contains__(self, term):
        return term in self._dict