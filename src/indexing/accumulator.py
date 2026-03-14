from pathlib import Path
from ..config.settings import ACCUMULATOR_THRESHOLD
from collections import defaultdict
# Used for extra credit ^^^
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

    # EXTRA CREDIT: changing the local_count types from dict[str, float] to dict[str, list[int]]
    def add_document(self, doc_id : int, local_positions : dict[str, list[int]]) -> None:
        '''
        Adds a new document to the index, increasing the term frequency
        for words from different documents.


        :param doc_id: Unique integer refencing a document
        :type doc_id: int
        :param local_positions: The counts of a word (i.e. {"twice" : 2, ...})
        :type local_positions: dict[str : list[int]]
        '''
        for term, positions in local_positions.items():
            if term not in self.index_map:
                self.index_map[term] = {}
            if doc_id not in self.index_map[term]:
                self.index_map[term][doc_id] = []
                self.postings_count += 1
            self.index_map[term][doc_id].extend(positions)
    
    def unique_terms(self) -> int:
        '''
        Return the number of terms saved within the index.
        
        :return: Number of terms within the index.
        :rtype: int
        '''
        return len(self.index_map)
    
    # build positions used for extra credit
    def build_positions(self, tokens):
        '''
        With a dictionary, maps the tokens with a term and list of
        positions where the term appears in the document.

        :param tokens: Ordered list of tokens from a document
        :type tokens: list[str]

        :return: Tokens from a given document containing the position
        :rtype: dict[str : list[int]]
        '''
        positions = defaultdict(list)
        for i, token in enumerate(tokens):
            positions[token].append(i)
        return dict(positions)
    
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
                    # EXTRA CREDIT
                    # instead of term : {docID:tf}, {docID:tf}
                    # Its now term: {docID:[pos,pos,pos]}
                    # Need to change postings_reader.py to convert string into list
                    positions = postings_dict[d]
                    pos_string = ",".join(str(p) for p in positions)
                    parts.append(f"{d}:{pos_string}")
                
                postings_string = " ".join(parts)

                out.write(f"{term}\t{postings_string}\n")
        
        self.index_map.clear()
        self.postings_count = 0
    
    def is_empty(self) -> bool:
        return len(self.index_map) == 0