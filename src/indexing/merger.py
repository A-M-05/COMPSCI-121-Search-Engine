import os
from .dictionary import DictionaryWrite
from ..config.settings import PARTIAL_PATH, MERGED_POSTINGS_PATH, DICTIONARY_PATH
import heapq

def parse_line(line: str) -> tuple[str, list[str]]:
    line = line.strip()
    if not line:
        return ("", [])

    parts = line.split("\t", 1)
    term = parts[0]

    if len(parts) < 2 or not parts[1].strip():
        return (term, [])

    postings_list = parts[1].split()
    return (term, postings_list)

def add_postings_to_accumulator(accumulator_dict : dict, postings_list : list[str]):
    for item in postings_list:
        doc_id_str, freq_str = item.split(":")
        doc_id = int(doc_id_str)
        positions = [int(p) for p in freq_str.split(',')]
        if doc_id in accumulator_dict:
            accumulator_dict[doc_id].extend(positions)
        else:
            accumulator_dict[doc_id] = positions
class Merger:
    def __init__(self):
        pass

    def merge_partials(self):
        # Collect and validate partial files
        partial_files = sorted(PARTIAL_PATH.glob("partial_*.tsv"))

        if not partial_files:
            print("ERROR: No partial files found.")
            return
        
        # Ensure output directory exists
        MERGED_POSTINGS_PATH.parent.mkdir(parents=True, exist_ok = True)
        DICTIONARY_PATH.parent.mkdir(parents=True, exist_ok = True)
        open(DICTIONARY_PATH, "w").close()   # Check if directories exists:   # In the case two mergers are being utilized, close dictionary file; avoids duplicate entries
        
        # Open all partial files
        file_handles = []
        for file_path in partial_files:
            file_handles.append(open(file_path, 'r'))

        # Initialize heap with first line from each file
        heap = []
        for file_id in range(0, len(file_handles)):
            line = file_handles[file_id].readline()
            if line:
                (term, postings_list) = parse_line(line)
                heapq.heappush(heap, (term, file_id, postings_list))
        
        # Open merged postings output
        merged_file = open(MERGED_POSTINGS_PATH, "w")
        dictionary_writer = DictionaryWrite()

        offset_bytes = 0
        
        # Merge loop
        while heap:
            # Pop smallest
            term, file_id, postings_list = heapq.heappop(heap)
            
            
            # Start accumulating postings for this term
            postings_accumulator = dict()
            add_postings_to_accumulator(postings_accumulator, postings_list)

            file_contribution = [file_id]

            # Pull all other heap entries that have the same term
            while heap and heap[0][0] == term:
                _, file_id2, postings_list2 = heapq.heappop(heap)
                add_postings_to_accumulator(postings_accumulator, postings_list2)
                file_contribution.append(file_id2)
            
            # Finalize postings: sort doc_ids and format postings list
            sorted_doc_ids = sorted(postings_accumulator.keys())
            
            final_postings_list = []
            for doc_id in sorted_doc_ids:
                positions = postings_accumulator[doc_id]
                pos_str = ','.join(str(p) for p in positions)
                final_postings_list.append(f"{doc_id}:{pos_str}")
            
            doc_freq = len(final_postings_list)

            # Write merged line
            merged_line_str = term + "\t" + " ".join(final_postings_list) + "\n"
            bytes_written = len(merged_line_str.encode("utf-8"))
            merged_file.write(merged_line_str)

            # Write dictionary entry
            dictionary_writer.write_entry(term, doc_freq, offset_bytes)
            offset_bytes += bytes_written
        
            # Advance each contributing file by one line and push onto heap
            for file_id in file_contribution:
                curr_line = file_handles[file_id].readline()

                if curr_line:
                    next_term, next_postings_list = parse_line(curr_line)
                    heapq.heappush(heap, (next_term, file_id, next_postings_list))
        
        # Close all files
        merged_file.close()
        dictionary_writer.close()
        for file in file_handles:
            file.close()
