# Słowosieć

**Słowosieć** is a browser-based Polish word association game powered by **word embeddings and graph algorithms**. The goal is to connect two words by building a network of intermediate associations. Connections are not manually defined: they are derived from the semantic relationships captured by a pretrained **fastText** model.

The project was developed as an interactive demonstration for a talk at the **Elements conference at AGH University of Krakow**. It brings together natural language processing, graph analysis, and a responsive web application.

> The game is an independent project inspired by [Linxicon](https://linxicon.com/). It demonstrates word embeddings and semantic graph traversal; **it is not a RAG implementation**.

## How to play

1. Start with the **green word on the left** and try to reach the **yellow target word on the right**.
2. Enter words to expand the network. A new word must be in the vocabulary and connected to at least one word already on the board.
3. Win by building a connected network that reaches the target.

The game also supports randomly generated word pairs, custom starting and target words, autocomplete, a searchable/browsable vocabulary, undo, and board reset. The interface works on both desktop and mobile devices.

## How it works

### 1. Word embeddings

The vocabulary is derived from Polish word-frequency data and filtered using morphological analysis and additional curation. Each retained word is represented by a **300-dimensional vector** from the pretrained Polish fastText model (`cc.pl.300.bin`).

For two words \(u\) and \(v\), their similarity is measured using cosine similarity:

$$
\mathrm{sim}(u,v) =
\frac{\mathbf{e}_u \cdot \mathbf{e}_v}
{\lVert \mathbf{e}_u \rVert \, \lVert \mathbf{e}_v \rVert}
$$

Words with similar distributional contexts tend to have nearby vectors, although vector similarity does not always match human intuition.

### 2. Building the semantic graph

Each word becomes a vertex in an **undirected graph**. An edge is added between two distinct words when **both** conditions are satisfied:

- Their cosine similarity is at least **0.40**.
- **At least one** of the words appears among the other's **25 nearest neighbors** (*union top-25*).

This differs from *mutual top-25*, which requires both words to appear in each other's top-25 lists. The final graph is stored as adjacency lists rather than a dense pairwise similarity matrix.

### 3. Running the game

The React application loads a precomputed graph from:

```text
public/data/graph_fasttext_mutual.json
```

The filename is historical: the current graph uses the **union top-25** strategy, not mutual top-25. Graph traversal and shortest-path calculations use **breadth-first search (BFS)**.

**The fastText model runs only during offline data preparation.** The playable website uses the exported JSON graph, so no ML model, backend, or external inference API is needed at runtime.

## Experiments and results

The development process involved two main comparisons:

- **MiniLM vs. fastText:** in manual evaluations of nearest neighbors for individual Polish nouns, fastText produced more useful associations for this game.
- **Mutual vs. union top-K graphs:** multiple neighborhood sizes and similarity thresholds were evaluated using connectivity statistics, shortest-path lengths, and gameplay tests.

### Mutual top-25 vs. union top-25

The following measurements come from an experiment on **5,602 words**, before a later small adjustment to the exclusion list. They describe the evaluated graph variants, not necessarily the exact counts in the latest deployed JSON file.

| Metric | Mutual top-25 (≥ 0.40) | Union top-25 (≥ 0.40) |
|---|---:|---:|
| Undirected edges | 38,161 | **76,364** |
| Average node degree | 13.62 | **27.26** |
| Isolated nodes | 126 | **89** |
| Nodes in the largest connected component | 97.38% | **98.27%** |
| Mean shortest-path length (sample) | 4.56 | **3.63** |
| Sampled pairs at distance 6+ | 15.31% | **1.24%** |

Shortest-path statistics were compared using the **same 818,100 ordered source–target pairs** in both variants (150 sampled source vertices and the remaining vertices of the baseline graph's largest connected component).

**Why union top-25?** It made useful associations easier to discover and reduced overly long paths while retaining a meaningful challenge. Informal gameplay tests also favored it over the sparser mutual graph. Increasing the number of neighbors further made the graph substantially denser, so union top-25 was selected as a compromise between connectivity and game difficulty.

### Known limitations

- Embedding similarity is statistical, not a guarantee of a human-recognizable association. Some intuitive word pairs may not have a direct edge.
- Other pairs can be connected for reasons that are not immediately obvious to a player.
- The vocabulary is filtered and finite; not every valid Polish word is available.
- No individual graph edges were manually added to fix specific word pairs.

## Tech stack

| Area | Technologies |
|---|---|
| Web application | React, TypeScript, Vite |
| Graph visualization | React Flow (`@xyflow/react`) |
| Data preparation | Python, NumPy, `wordfreq`, Morfeusz |
| Word representations | fastText (final); MiniLM (experimental) |
| Graph analysis | BFS, NumPy, SciPy |
| Deployment | Netlify (static hosting) |

## Getting started

**Requirements:** Node.js and npm.

The frontend is in the `slowosiec/` subdirectory of the repository:

```bash
git clone https://github.com/Carrot516/slowosiec.git
cd slowosiec/slowosiec
npm install
npm run dev
```

Open the local URL printed by Vite. The development server is configured to listen on `0.0.0.0`, so run it only on a trusted network.

### Production build

```bash
npm run build
npm run preview
```

The generated `dist/` directory can be deployed to a static hosting provider such as Netlify. Python and the fastText model are **not** required to run or build the frontend, provided the precomputed graph JSON is present.

## Repository structure

```text
README.md
slowosiec/
├── src/
│   ├── components/        # Game UI, word browser, and autocomplete
│   ├── game/              # Graph utilities, BFS, and word-pair generation
│   ├── App.tsx
│   └── App.css
├── public/
│   └── data/
│       └── graph_fasttext_mutual.json
├── scripts/               # NLP preprocessing and graph experiments
├── package.json
└── vite.config.ts
```

The `scripts/` directory contains the 12 retained research and preprocessing scripts:

| Stage | Scripts |
|---|---|
| Vocabulary preparation | `generate_words.py`, `filter_fasttext_words.py` |
| Embedding generation | `generate_embeddings.py`, `generate_fasttext_embeddings.py` |
| Embedding evaluation | `compare_models.py`, `analyze_embeddings.py` |
| Graph construction experiments | `compare_graph_variants.py`, `compare_union_graphs.py` |
| Graph diagnostics | `analyze_graph.py`, `analyze_word_pairs.py`, `analyze_distances.py`, `compare_graph_distances.py` |

### Reproducing the data pipeline

The playable graph is included in the repository, but **the full preprocessing pipeline is not self-contained**. Large pretrained models (`models/`), intermediate experimental outputs (`data/`), and the local word exclusion list (`scripts/excluded_words.txt`) are not published. Reproducing the complete graph-building process therefore requires obtaining the relevant inputs and the [Polish fastText model](https://fasttext.cc/docs/en/crawl-vectors.html).

This limitation does **not** affect running the game from the committed graph JSON.

## Acknowledgments

- [Linxicon](https://linxicon.com/) — inspiration for the word-association gameplay.
- [fastText](https://fasttext.cc/) — pretrained word embeddings.
- [React Flow](https://reactflow.dev/) — interactive graph visualization.

Słowosieć is an independent educational project and is not affiliated with Linxicon.
