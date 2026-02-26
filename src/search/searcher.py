from ..text.tokstem import normalize
from .dictionary_reader import DictionaryReader
from .postings_reader import PostingsReader
from .doc_table_reader import DocTableReader


def _intersect_two(list_a, list_b):
        # Going to walk through the two SORTED lists
        result = []
        i, j = 0, 0
        while i < len(list_a) and j < len(list_b):
            if list_a[i] == list_b[j]:
                # Keep the doc id if theyre the same in both lists
                result.append(list_a[i])
                i += 1
                j += 1
            elif list_a[i] < list_b[j]:
                i += 1
            else:
                j += 1
        return result

class Searcher:
    def __init__(self):
        # Just to see what exactly its doing
        print('loading index')
        self._dictionary = DictionaryReader()
        self._postings = PostingsReader()
        self._doc_table = DocTableReader()
        print('ready')

    # top_k just represents _ # top URLS
    def search(self, query, top_k = 15):
        terms = normalize(query)
        print(f'Searching for terms: {terms}')
        if not terms:
            return []
        
        postings_lists = []
        for term in terms:
            entry = self._dictionary.lookup(term)
            if entry is None:
                return []
            # _ represents doc freq, offset is byte position where line starts
            _, offset = entry
            raw = self._postings.get_postings(offset)
            doc_ids = [doc_id for doc_id, _ in raw]
            # ^ Gets first value from the tuple that contains the doc id + weighted freq
            # Pulls out the first value from each tuple - ignoring the freq
            postings_lists.append(doc_ids)
        postings_lists.sort(key = len)
        # ^ Sortings shortest list first

        result = postings_lists[0]
        for i in range(1, len(postings_lists)):
            result = _intersect_two(result, postings_lists[i])
            if not result:
                # No point continuing if its already empty
                return []
        
        # Mapping the doc ids to their urls for the top _# urls
        urls = []
        for doc_id in result[:top_k]:
            url = self._doc_table.get_url(doc_id)
            if url:
                urls.append(url)
        return urls
        
    def close(self):
        self._postings.close()
