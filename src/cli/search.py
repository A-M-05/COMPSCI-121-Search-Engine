from ..search.searcher import Searcher

def search():
    searcher = Searcher()

    print("Type 'quit' to quit")
    
    while True:
        query = input("Query: ").strip()

        if not query:
            continue     
        if query.lower() == 'quit':
            break
        
        results = searcher.search(query, top_k = 15)

        if not results:
            print('no results :P\n')
        else:
            print(f'Top {len(results)} results: ')
            for i in range(len(results)):
                print(f'.  {i+1}. {results[i]}')
            print()

    searcher.close()
