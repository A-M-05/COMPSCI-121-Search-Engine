from pathlib import Path
from ..config.settings import ACCUMULATOR_THRESHOLD
# Make threshold higher - 50 is temporary
class IndexAccumulator:
    def __init__(self):
        self.index_map = {}
        self.postings_count = 0
        self.threshold = ACCUMULATOR_THRESHOLD
    
    def define_threshold(self, threshold: int) -> None:
        '''
        Defines Threshold. Utilized for when the posting count
        becomes too large.

        :param threshold: Integer referencing the limit of posting counts
        :type threshold: int
        '''
        self.threshold = threshold

    def add_document(self, doc_id : int, local_counts : dict[str, float]) -> None:
        '''
        Adds a new document to the index, increasing the term frequency
        for words from different documents.


        :param doc_id: Unique integer refencing a document
        :type doc_id: int
        :param local_counts: The counts of a word (i.e. {"twice" : 2, ...})
        :type local_counts: dict
        '''
        for term, freq in local_counts.items():
            if term not in self.index_map:
                self.index_map[term] = {}
            if doc_id not in self.index_map[term]:
                self.index_map[term][doc_id] = 0.0
                self.postings_count += 1
            self.index_map[term][doc_id] += freq
    
    def unique_terms(self) -> int:
        '''
        Return the number of terms saved within the index.
        
        :return: Number of terms within the index.
        :rtype: int
        '''
        return len(self.index_map)
    
    def should_flush(self) -> bool:
        '''
        If the current number of elements within the index
        is larger than the defined threshold, return true.
        Otherwise, return false.
        
        :return: If posting count is larger or equal to threshold
        :rtype: bool
        '''
        return self.postings_count >= self.threshold
    
    def flush(self, output_path : Path):
        if len(self.index_map) == 0:
            return
        
        with open(output_path, "w") as out:
            terms = sorted(self.index_map.keys())

            for term in terms:
                postings_dict = self.index_map[term]

                doc_ids = sorted(postings_dict.keys())

                parts = []
                for d in doc_ids:
                    tf = postings_dict[d]
                    parts.append(f"{d}:{tf}")
                
                postings_string = " ".join(parts)

                out.write(f"{term}\t{postings_string}\n")
        
        self.index_map.clear()
        self.postings_count = 0
    
    def is_empty(self) -> bool:
        return len(self.index_map) == 0