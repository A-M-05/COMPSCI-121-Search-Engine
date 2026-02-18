import os
import json
import re
from bs4 import BeautifulSoup


def tokenizer(text_content: str) -> list[str]:
    """
    Returns tokens INCLUDING stopwords (excluding pure digits).
    Used to compute stopword frequencies.
    """

    # 
    current = []
    tokens = []

    text_lower = text_content.lower()

    for char in text_lower:
        if char.isalnum() and char.isascii():
            current.append(char)
        else:
            if current:
                token = ''.join(current)
                if token and not token.isdigit():
                    tokens.append(token)
                current = []

    if current:
        token = ''.join(current)
        if token and not token.isdigit():
            tokens.append(token)

    return tokens


class InvertedIndexBuilder:
    def __init__(self):
        self.index = {}
        self.doc_count = 0
    
    def build_index(self, root_path):
        for root, dirs, files in os.walk(root_path):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    self.process_file(file_path)

    def process_file(self, file_path):
        # 1. Open the JSON file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
            html_content = data.get("content", "")

        # 2. Extract text with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
        #Without these lines above soup.get_text() would treat code as actual English text which would lead to thousands of "junk" tokens appearing.
        text = soup.get_text()

        # 3. Uses our tokenizer
        tokens = tokenizer(text)

        # 4. Assign a DocID and increment the counter
        doc_id = self.doc_count
        self.doc_count += 1

        # 5. Count Term Frequency (TF) for THIS document
        local_counts = {}
        for t in tokens:
            local_counts[t] = local_counts.get(t, 0) + 1

        # 6. Update the global index
        for token, tf in local_counts.items():
            if token not in self.index:
                self.index[token] = []
            # Add the posting: [DocID, Term Frequency]
            self.index[token].append([doc_id, tf])

if __name__ == "__main__":
    builder = InvertedIndexBuilder()
    builder.build_index("Assignment 3/DEV")

    with open("inverted_index.json", "w") as f:
        json.dump(builder.index, f)

    print(f"Number of indexed documents: {builder.doc_count}")
    print(f"Number of unique tokens: {len(builder.index)}")
    
    size_kb = os.path.getsize("inverted_index.json") / 1024
    print(f"Total size on disk: {size_kb:.2f} KB")