from nltk.stem.snowball import SnowballStemmer

def tokenize(text_content: str) -> list[str]:
    current = []
    tokens = []

    text_lower = text_content.lower()

    for char in text_lower:
        if char.isalnum():
            current.append(char)
        else:
            if current:
                tokens.append(''.join(current))
                current = []

    if current:
        tokens.append(''.join(current))

    return tokens

stemmer = SnowballStemmer("english")

def stem_tokens(tokens: list[str]) -> list[str]:
    return [stemmer.stem(token) for token in tokens]


def normalize(content: str) -> list[str]:
    tokens = tokenize(content)
    return stem_tokens(tokens)
