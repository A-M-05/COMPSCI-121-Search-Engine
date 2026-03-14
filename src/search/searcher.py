from ..config.settings import BETA, PAGERANK_SCORE_WEIGHT
from ..text.tokstem import normalize
from .dictionary_reader import DictionaryReader
from .postings_reader import PostingsReader
from .doc_table_reader import DocTableReader
from .doc_lengths_reader import DocLengthsReader
from .collection_stats_reader import CollectionStatsReader
from .bigram_reader import BigramReader
from .pagerank_reader import PageRankReader
import math
import heapq


class Searcher:
    def __init__(self):
        print("Loading index:")
        print("\tLoading dictionary...")
        self._dictionary = DictionaryReader()

        print("\tLoading postings...")
        self._postings = PostingsReader()

        print("\tLoading doc table...")
        self._doc_table = DocTableReader()

        print("\tLoading doc lengths...")
        self._doc_lengths = DocLengthsReader()

        print("\tLoading stats...")
        self._stats = CollectionStatsReader()

        print("\tLoading bigrams...")
        self._bigrams = BigramReader()

        print("\tLoading pagerank...")
        self._pagerank = PageRankReader()
        print("Ready.")

    def phrase_match(self, position_one: list[int], position_two: list[int]) -> bool:
        """
        Return True if any position in position_two immediately follows
        a position in position_one.

        :param position_one: Positions of first term
        :type position_one: list[int]
        :param position_two: Positions of second term
        :type position_two: list[int]
        :return: Whether the two terms appear adjacently
        :rtype: bool
        """
        index_one = 0
        index_two = 0

        while index_one < len(position_one) and index_two < len(position_two):
            diff = position_two[index_two] - position_one[index_one]

            if diff == 1:
                return True
            elif diff > 1:
                index_one += 1
            else:
                index_two += 1

        return False

    def search(self, query: str, top_k: int = 15) -> list[str]:
        # Step 1: Normalize query
        terms = normalize(query)

        print(f"Searching for terms: {terms}")
        if not terms:
            return []

        # Step 2: Count repeated query terms
        query_term_counts = {}
        for term in terms:
            query_term_counts[term] = query_term_counts.get(term, 0) + 1

        # Step 3: Gather query term metadata
        n = self._stats.total_docs()
        if n <= 0:
            return []

        term_infos = []
        for term, qtf in query_term_counts.items():
            entry = self._dictionary.lookup(term)
            if entry is None:
                continue

            df, offset = entry
            if df <= 0:
                continue

            idf = math.log10(n / df)
            term_infos.append((term, qtf, df, idf, offset))

        if not term_infos:
            return []

        # Step 4: Sort query terms by descending idf
        term_infos.sort(key=lambda x: x[3], reverse=True)

        # Step 5: Score accumulation
        scores = {}
        matched_terms = {}
        doc_positions = {}

        # tuple structure: (term, qtf, df, idf, offset)
        for term, qtf, _, idf, offset in term_infos:
            postings = self._postings.get_postings(offset)
            query_weight = (1 + math.log10(qtf)) * idf

            for doc_id, positions in postings:
                doc_positions.setdefault(doc_id, {})[term] = positions

                term_frequency = len(positions)
                if term_frequency > 0:
                    doc_weight = 1 + math.log10(term_frequency)
                else:
                    doc_weight = 0.0

                scores[doc_id] = scores.get(doc_id, 0.0) + (doc_weight * query_weight)
                matched_terms[doc_id] = matched_terms.get(doc_id, 0) + 1

        if not scores:
            return []

        # Step 6: Normalize by doc length
        for doc_id in scores:
            length = self._doc_lengths.get_length(doc_id)
            if length > 0:
                scores[doc_id] /= length

        # Step 7(a): Soft conjunction bonus
        for doc_id in scores:
            scores[doc_id] += BETA * matched_terms[doc_id]

        # Step 7(b): Bigram boost
        if len(terms) >= 2:
            for i in range(len(terms) - 1):
                bigram = terms[i] + "_" + terms[i + 1]
                matching_docs = self._bigrams.get_docs(bigram)

                for doc_id in matching_docs:
                    if doc_id in scores:
                        scores[doc_id] += 0.5

        # Step 7(c): Phrase positional boost
        if len(terms) >= 2:
            for doc_id in scores:
                if doc_id not in doc_positions:
                    continue

                term_map = doc_positions[doc_id]

                for i in range(len(terms) - 1):
                    t1 = terms[i]
                    t2 = terms[i + 1]

                    if t1 in term_map and t2 in term_map:
                        if self.phrase_match(term_map[t1], term_map[t2]):
                            scores[doc_id] += 1.0

        # Step 7(d): PageRank boost
        for doc_id in scores:
            pagerank_score = self._pagerank.get_score(doc_id)
            scores[doc_id] += PAGERANK_SCORE_WEIGHT * pagerank_score

        # Step 8: Pick top K with heap
        top_docs = heapq.nlargest(top_k, scores.items(), key=lambda x: x[1])

        urls = []
        for doc_id, score in top_docs:
            url = self._doc_table.get_url(doc_id)
            if url:
                urls.append(url)

        return urls

    def close(self) -> None:
        self._postings.close()