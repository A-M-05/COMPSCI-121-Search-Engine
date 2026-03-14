from ..config.settings import MERGED_POSTINGS_PATH

class PostingsReader:
    def __init__(self):
        if not MERGED_POSTINGS_PATH.exists():
            raise FileNotFoundError(f'Postings file not found at {MERGED_POSTINGS_PATH}')
        self._file = open(MERGED_POSTINGS_PATH, 'rb')

    def get_postings(self, offset):
        self._file.seek(offset)
        line = self._file.readline().decode('utf-8').strip()
        # Seek just jumps directly to the byte position, no scanning
        # Only reading one line for a very big file

        if not line:
            return []
        parts = line.split('\t', 1)
        if len(parts) < 2:
            return []
        
        postings = []
        for item in parts[1].split():
            doc_id_str, pos_str = item.split(':')
            doc_id = int (doc_id_str)
            positions = [int (p) for p in pos_str.split(',')]
            # EXTRA CREDIT T3: changed the postings to be doc_id, [positions]
            postings.append((doc_id, positions))
        return postings
    
        # parts[1] = postings side of the line
        # Looks like: doc2:3.0 doc7:1.0
        # Split on whitespace to get each docid & freq pair

    def close(self):
        self._file.close()
