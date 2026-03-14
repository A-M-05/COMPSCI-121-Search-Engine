from ..config.settings import GRAPH_EDGES_PATH, COLLECTION_STATS_PATH, PAGERANK_PATH, PAGERANK_ALPHA, PAGERANK_ITERATIONS

def load_total_docs():
    if not COLLECTION_STATS_PATH.exists():
        raise FileNotFoundError
    
    with open(COLLECTION_STATS_PATH, "r") as collection_stats:
        for line in collection_stats:
            line = line.strip()

            if not line:
                continue

            parts = line.split('\t', 1)
            if len(parts) != 2:
                continue
            key, value = parts[0], parts[1]

            if key == "total_docs":
                return int(value)
            
    raise ValueError

def load_graph(n : int):
    if not GRAPH_EDGES_PATH.exists():
        raise FileNotFoundError
    
    outgoing = [set() for _ in range(n)]
    outdegree = [0] * n

    with open(GRAPH_EDGES_PATH, "r") as graph_edges:
        for line in graph_edges:
            line = line.strip()

            if not line:
                continue

            parts = line.split('\t', 1)
            if len(parts) != 2:
                continue
            source_doc_id, target_doc_id = int(parts[0]), int(parts[1])

            if not ((0 <= source_doc_id < n) and (0 <= target_doc_id < n)):
                continue

            if target_doc_id not in outgoing[source_doc_id]:
                outgoing[source_doc_id].add(target_doc_id)
                outdegree[source_doc_id] += 1

    return (outgoing, outdegree)

def compute_pagerank(n : int, outgoing, outdegree):
    alpha = PAGERANK_ALPHA
    iterations = PAGERANK_ITERATIONS

    rank = [1.0 / n] * n

    for i in range(iterations):
        new_rank = [(1.0 - alpha) / n] * n

        dangling_mass = 0.0

        for doc_u in range(n):
            if outdegree[doc_u] == 0:
                dangling_mass += rank[doc_u]
            else:
                contribution = alpha * rank[doc_u] / outdegree[doc_u]
                for target_v in outgoing[doc_u]:
                    new_rank[target_v] += contribution
        
        dangling_share = alpha * dangling_mass / n

        for doc_d in range(n):
            new_rank[doc_d] += dangling_share

        rank = new_rank
    
    return rank

def write_pagerank(rank : list[float]):
    PAGERANK_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(PAGERANK_PATH, "w") as pagerank_table:
        for doc_id in range(len(rank)):
            pagerank_table.write(f"{doc_id}\t{rank[doc_id]}\n")

def build_pagerank():
    n = load_total_docs()
    outgoing, outdegree = load_graph(n)

    total_edges = sum(len(neighbors) for neighbors in outgoing)

    rank = compute_pagerank(n, outgoing, outdegree)
    write_pagerank(rank)

    rank_sum = sum(rank)

    print("PageRank Summary:")
    print(f"\tTotal Documents:     {n}")
    print(f"\tTotal Edges:         {total_edges}")
    print(f"\tAlpha:               {PAGERANK_ALPHA}")
    print(f"\tIterations:          {PAGERANK_ITERATIONS}")
    print(f"\tOutput Path:         {PAGERANK_PATH}")
    print(f"\tPageRank Scores Sum: {rank_sum}")

if __name__ == "__main__":
    build_pagerank()