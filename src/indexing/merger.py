import os
from .dictionary import DictionaryWrite
from ..config.settings import PARTIAL_PATH, MERGED_POSTINGS_PATH


def get_smallest_term(curlist: list[tuple]) -> tuple:
    '''
    Get the smallest lexicographical term from the list
    
    :param curlist: Contains a list of tuples
    :type curlist: list[tuple]
    :param curlist[tuple]: (term, fileIndex, [{id:freq}])
    :return: Description
    :rtype: tuple
    '''
    smallestTerm = curlist[0]
    for curTuple in curlist:
        if (curTuple[0] < smallestTerm[0]):
            smallestTerm = curTuple
    return smallestTerm

def listToDict(curList: list[str]) -> dict[int, float]:
    newDict = {}
    for docInfo in curList:
        elements = docInfo.split(":")
        newDict[int(elements[0])] = float(elements[1])
    return newDict

def mergeLists(baseList: list[str], newList: list[str]) -> list[str]:
    '''
    Merge two lists into one
    
    :param baseList: Original List (curPostingList) | ["3:1", "5:2", ...]
    :type baseList: list[str]
    :param newList: New List (next_tuple[2]) | ["3:1", "5:2", ...]
    :type newList: list[str]
    :return: Combination of the two lists without duplicates
    :rtype: list[str]
    '''
    baseDict = listToDict(baseList)
    newDict = listToDict(newList)

    for key, value in newDict.items():
        if (key in baseDict):
            baseDict[key] += value
        else:
            baseDict[key] = value

    sorted_doc_ids = sorted(baseDict.keys())

    returnList = []
    for doc_id in sorted_doc_ids:
        returnList.append(f"{doc_id}:{baseDict[doc_id]}")
    return returnList
    

class Merger:
    def __init__(self):
        pass

    def merge_partials(self):
        partial_paths = []
        heap = []
        for path, _, fileNames in os.walk("./partials"):
            for fileName in fileNames:
                cur_path = os.path.join(path, fileName)
                partial_paths.append(cur_path)
        partial_paths = sorted(partial_paths)
        
        opened_paths = []
        for path in partial_paths:
            opened_paths.append(open(path, 'r'))

        file_index = 0
        for open_file in opened_paths:
            first_line = open_file.readline()
            if (first_line):
                parsed = first_line.strip().split()
                heap.append((parsed[0], file_index, parsed[1:]))
            file_index += 1

        
        final_file = open("./postings/output.txt", "w")
        dictionaryInstance = DictionaryWrite()
        current_offset = 0
        open("./dictionary/entries", "w").close()   # In the case two mergers are being utilized, close dictionary file; avoids duplicate entries
        while (heap):
            term_tuple = get_smallest_term(heap)
            heap.remove(term_tuple)
            curTerm, curFileId, curPostingList = term_tuple[0], term_tuple[1], term_tuple[2]
            file_contribution = [curFileId]
            index = 0
            while index < len(heap):
                if (heap[index][0] == curTerm):
                    tuple_chosen = heap[index]
                    curPostingList = mergeLists(curPostingList, tuple_chosen[2])
                    file_contribution.append(tuple_chosen[1])
                    heap.pop(index)
                else:
                    index += 1
            
            save_offset = current_offset
            line = curTerm + " " + " ".join(curPostingList) + "\n"
            bytes_written = final_file.write(line)
            current_offset += bytes_written

            docFreq = len(curPostingList)
            dictionaryInstance.write_entry(curTerm, docFreq, save_offset)
        
            for file_id in file_contribution:
                curLine = opened_paths[file_id].readline()

                if curLine:
                    parsed = curLine.strip().split()
                    heap.append((parsed[0], file_id, parsed[1:]))
        
        final_file.close()
        for file in opened_paths:
            file.close()

