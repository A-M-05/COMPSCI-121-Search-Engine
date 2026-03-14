from ..config.settings import PAGERANK_PATH


class PageRankReader:
    def __init__(self):
        self._scores = []
        self._file = PAGERANK_PATH
        self.load()

    def load(self) -> None:
        if not self._file.exists():
            raise FileNotFoundError(f"PageRank file not found at {self._file}")

        with open(self._file, "r", encoding="utf-8") as pagerank_file:
            for line in pagerank_file:
                line = line.strip()
                if not line:
                    continue

                parts = line.split("\t", 1)
                if len(parts) != 2:
                    continue

                doc_id = int(parts[0])
                score = float(parts[1])

                if doc_id >= len(self._scores):
                    self._scores.extend([0.0] * (doc_id + 1 - len(self._scores)))

                self._scores[doc_id] = score

    def get_score(self, doc_id: int) -> float:
        if 0 <= doc_id < len(self._scores):
            return self._scores[doc_id]
        return 0.0