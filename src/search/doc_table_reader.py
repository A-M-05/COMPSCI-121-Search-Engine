from ..config.settings import DOC_TABLE_PATH

class DocTableReader:
    def __init__(self):
        # We don't need a dict bc doc ids are just integers which is faster
        # than dictionary
        self._urls = []
        self._load()
    
    def _load(self):
        if not DOC_TABLE_PATH.exists():
            raise FileNotFoundError(f'Doc table not found at {DOC_TABLE_PATH}')
        
        with open(DOC_TABLE_PATH, 'r', encoding = 'utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split('\t', 1)
                if len(parts) != 2:
                    continue

                doc_id = int(parts[0])
                url = parts[1]
                
                # extend the list until index doc_id exists
                # ^ bc doc_ids can be out of order or have gaps
                while len(self._urls) <= doc_id:
                    self._urls.append('')

                self._urls[doc_id] = url
                # Each line would look something like:
                # 5\thttps://ics.uci.edu/...
                # So it will split on the tab, take the doc_id and url,
                # and add it to the list
    
    def get_url(self, doc_id):
        if doc_id < len(self._urls):
            return self._urls[doc_id]
        return ''
