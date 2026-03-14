# COMPSCI 121 Search Engine

## Overview

This Search Engine is a full-text search engine developed for COMPSCI 121 at UC Irvine.  
It supports ranked retrieval over a large web corpus using an inverted index, tf-idf weighting, positional scoring, duplicate detection, and PageRank.  
The system includes both a command-line pipeline and a graphical interface for interactive querying.

This project demonstrates the complete search engine workflow:

- Crawled dataset processing  
- Indexing and ranking  
- Link analysis (PageRank)  
- Near-duplicate detection  
- Query-time ranking and boosting  
- UI-based search experience  

---

## Authors

- Jasnoor Sekhon — 81152829  
- Kenneth Albarillo — 32511318  
- Nicholas Quach — 43314317  
- Abraham Manu — 26411611  

---

## Features

### Core Retrieval

- Inverted index with tf-idf ranking  
- Cosine normalization using document length  
- Query weighting with logarithmic tf scaling  

### Ranking Improvements

- PageRank integration for authority scoring  
- Soft conjunction boosting for multi-term matches  
- Positional scoring for phrase-sensitive ranking  
- Bigram proximity boosting  

### Data Quality Handling

- Exact duplicate detection using hashing  
- Near-duplicate detection using SimHash  

### Performance

- Partial indexing with merging  
- Efficient postings access via byte offsets  
- Optimized pipeline workflow  

### Interface

- Command-line search  
- Tkinter graphical search UI  
- Clickable results with browser launch  

---

## How to Run

### 1. Run Full Pipeline

This builds the index, link graph, and PageRank automatically (skipping completed steps):

```bash
python -m src.cli.pipeline
```

### 2. Run CLI Search Only

```bash
python -m src.cli.search
```

### 3. Run Graphical Interface

```bash
python ui.py
```

---

## Pipeline Workflow

The pipeline performs:

1. Index Construction
    - HTML parsing
    - Tokenization + stemming
    - tf-idf weighting
    - Positional indexing
2. Duplicate Detection
    - Exact duplicates via hashing
    - Near duplicates via SimHash
3. Link Graph Construction
4. PageRank Computation
5. Interactive Search
