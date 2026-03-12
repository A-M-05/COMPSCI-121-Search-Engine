from ..config.settings import BETA
from ..text.tokstem import normalize
from .dictionary_reader import DictionaryReader
from .postings_reader import PostingsReader
from .doc_table_reader import DocTableReader
from .doc_lengths_reader import DocLengthsReader
from .collection_stats_reader import CollectionStatsReader
import math, heapq

class Searcher:
    def __init__(self):
        # Just to see what exactly its doing
        print("Loading index:")
        self._dictionary = DictionaryReader()
        self._postings = PostingsReader()
        self._doc_table = DocTableReader()
        self._doc_lengths = DocLengthsReader()
        self._stats = CollectionStatsReader()
        print("Ready.")

    # top_k just represents _ # top URLS
    def search(self, query, top_k = 15):
        
        # Step 1: Normalize query
        terms = normalize(query)

        print(f"Searching for terms: {terms}")
        if not terms:
            return []
        

        # Step 2: Count repeated query terms
        query_term_counts = {}
        for term in terms:
            if term in query_term_counts:
                query_term_counts[term] += 1
            else:
                query_term_counts[term] = 1


        # Step 3: Gather meta data
        n = self._stats.total_docs()
        term_infos = []

        for term in query_term_counts:
            entry = self._dictionary.lookup(term)
            if entry is None:
                continue
            
            df, offset = entry
            if df <= 0:
                continue
            
            x = float(n / df)
            idf = math.log10(x)

            term_infos.append((term, query_term_counts[term], df, idf, offset))
        
        if not term_infos:
            return []


        # Step 4: Sort query terms by descending idf
        term_infos.sort(key = lambda x: x[3], reverse = True)
        

        # Step 5: Score accumulation
        scores = {}
        matched_terms = {}
        # tuple structure: (term, gtf, df, idf, offset)
        for (term, qtf, _, idf, offset) in term_infos:
            
            postings = self._postings.get_postings(offset)
            query_weight = (1 + math.log10(qtf)) * idf
            
            for (doc_id, weighted_tf_td) in postings:
                if weighted_tf_td > 0:
                    doc_weight = 1 + math.log10(weighted_tf_td)
                else:
                    doc_weight = 0
                scores[doc_id] = scores.get(doc_id, 0) + doc_weight * query_weight
                matched_terms[doc_id] = matched_terms.get(doc_id, 0) + 1
        

        # Step 6: Normalize by doc length
        for doc_id in scores:
            length = self._doc_lengths.get_length(doc_id)
            if length > 0:
                scores[doc_id] /= length
        
        # Step 7: Soft conjunction bonus
        for doc_id in scores:
            scores[doc_id] += BETA * matched_terms[doc_id]


        # Step 8: Pick top K with heap
        top_docs = heapq.nlargest(top_k, scores.items(), key = lambda x: x[1])

        urls = []
        for (docid, score) in top_docs:
            url = self._doc_table.get_url(docid)
            if url:
                urls.append(url)
        
        return urls
        
    def close(self):
        self._postings.close()
