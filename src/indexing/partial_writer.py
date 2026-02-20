
class PartialWriter:

    def __init__(self):
        pass

    def write_partial(self, index: dict[str:dict[int:int]], spill_number: int) -> None:
        '''
        Adds document ID to the terms stored within a given file.
        
        :param index: Current Index
        :type index: dict
        :param spill_number: Current spill number
        :type spill_number: int
        '''
        sorted_terms = {}
        file = f"./partials/partial_{spill_number}.idx"
        with open(file, 'w') as partialFile:
            lowestTerms = sorted(index.keys())
            for term in lowestTerms:
                sorted_terms = index[term]
                doc_ids = sorted(sorted_terms.keys())
                curLine = term
                for doc_id in doc_ids:
                    termFreq = sorted_terms[doc_id]
                    curLine += f" {doc_id}:{termFreq}"
                curLine += '\n'
                partialFile.write(curLine)
