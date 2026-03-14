from ..config.settings import BIGRAM_INDEX_PATH

class BigramReader:
    def __init__(self):
        # dict where key = bigram, value = set of doc_ids that contain it
        self._index = {}
        self._load()

    def _load(self):
        # If file doesn't exist, stop immediately
        if not BIGRAM_INDEX_PATH.exists():
            raise FileNotFoundError(f"[DEBUG] Bigram index not found at {BIGRAM_INDEX_PATH}")
        
        # Open file and read it line by line
        with open(BIGRAM_INDEX_PATH, 'r', encoding = 'utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Each line looks like '5\tmachin_learn'
                # Split on the tab to get [doc_id, bigram]
                parts = line.split('\t', 1)
                if len(parts) != 2:
                    continue

                doc_id = int(parts[0])
                bigram = parts[1]

                # If we haven't seen this bigram before, create empty set for it
                if bigram not in self._index:
                    self._index[bigram] = set()
                
                # Add this doc_id to the set of docs containing this bigram
                self._index[bigram].add(doc_id)
    
    def get_docs(self, bigram: str) -> set:
        # Return the set of doc_ids that contain this bigram
        # If bigram not found, return empty set
        return self._index.get(bigram, set())
