from ..config.settings import DOC_LENGTHS_PATH

class DocLengthsReader:
    def __init__(self):
        # list where index = doc_id, value = its length
        self._lengths = []
        self._load()
    
    def _load(self):
        # If file doesn't exist, stop immediately
        if not DOC_LENGTHS_PATH.exists():
            raise FileNotFoundError(f'[DEBUG] Doc lengths file not found at {DOC_LENGTHS_PATH}')

        with open(DOC_LENGTHS_PATH, 'r', encoding = 'utf-8') as f:
            for line in f:
                line = line.strip()  # Removing extra whitespace/new lines
                if not line: # Skipping empty lines
                    continue

                # Each doc looks like: "0\t2.45"
                # Split on teh tab to get the [doc_id, doc_length]
                parts = line.split('\t', 1)
                if len(parts) != 2:
                    continue 
                
                doc_id = int(parts[0])
                doc_length = float(parts[1])

                # Extend the list with 1.0 as default until doc_id index exists
                # Possible that docid is bigger than current list size
                while len(self._lengths) <= doc_id:
                    self._lengths.append(1.0)
                
                # Store actual length at that index
                self._lengths[doc_id] = doc_length
            
    def get_length(self, doc_id):
        # Check to see if doc_id is within the range of the list
        if 0 <= doc_id < len(self._lengths):
            return self._lengths[doc_id]
        return 1.0 # Fallback if the docid isnt found so we dont divide by 0 on accident
