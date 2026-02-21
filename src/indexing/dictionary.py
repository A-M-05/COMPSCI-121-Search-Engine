'''
Writes entries of the term, number of documents that contain the term, and the offset.
'''

from ..config.settings import DICTIONARY_PATH

class DictionaryWrite:

    def __init__(self):
        self.file = DICTIONARY_PATH
    
    def write_entry(self, term: str, doc_count:int, offset: int):
        '''
        Writes the format: term document_count offset
        into a given file path
        
        :param term: Word/term stored within the documents
        :type term: str
        :param doc_count: Number of documents containing the word
        :type doc_count: int
        :param offset: Beginning of term's post within the given posting
        :type offset: int
        '''
        with open(self.file, 'a') as entryFile:
            line = f"{term} {doc_count} {offset}\n"
            entryFile.write(line)
