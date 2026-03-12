
from ..config.settings import COLLECTION_STATS_PATH

class CollectionStatsReader:
    def __init__(self):
        self._total_docs = 0
        self._load()
    
    def _load(self):
        if not COLLECTION_STATS_PATH.exists():
            raise FileNotFoundError(f'[DEBUG] Collection stats file not found at {COLLECTION_STATS_PATH}')
        
        with open(COLLECTION_STATS_PATH, 'r') as collection:
            for line in collection:
                line = line.strip()
                if not line:
                    continue
                curLine = line.split('\t')
                if (curLine[0] == "total_docs"):
                    self._total_docs = int(curLine[1])

    def total_docs(self):
        return self._total_docs
