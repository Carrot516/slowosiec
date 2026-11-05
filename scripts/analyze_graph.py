
import json
from pathlib import Path

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "public" / "data"

THRESHOLDS = [0.4, 0.5, 0.6, 0.7, 0.8]


def analyze_threshold(embeddings, threshold):
    n = len(embeddings)

    rows = []
    cols = []

    # Obliczamy podobieństwa partiami,
    # aby nie przechowywać całej macierzy NxN.
    batch_size = 256

    for start in range(0, n, batch_size):
        end = min(start + batch_size, n)

        similarities = embeddings[start:end] @ embeddings.T

        for local_i, global_i in enumerate(range(start, end)):
            # Tylko górny trójkąt macierzy.
            neighbors = np.where(
                similarities[local_i, global_i + 1:] >= threshold
            )[0] + global_i + 1

            for j in neighbors:
                rows.extend([global_i, int(j)])
                cols.extend([int(j), global_i])

    data = np.ones(len(rows), dtype=np.uint8)

    graph = csr_matrix(
        (data, (rows, cols)),
        shape=(n, n)
    )

    degrees = np.diff(graph.indptr)

    components_count, labels = connected_components(
        graph,
        directed=False
    )

    component_sizes = np.bincount(labels)

    return {
        "threshold": threshold,
        "edges": graph.nnz // 2,
        "avg_degree": float(np.mean(degrees)),
        "isolated": int(np.sum(degrees == 0)),
        "components": int(components_count),
        "largest_component": int(np.max(component_sizes)),
    }


def main():
    with (DATA_DIR / "embedding_words.json").open(
        encoding="utf-8"
    ) as file:
        words = json.load(file)

    embeddings = np.load(DATA_DIR / "embeddings.npy")

    if len(words) != len(embeddings):
        raise ValueError("Niezgodna liczba słów i embeddingów.")

    for threshold in THRESHOLDS:
        result = analyze_threshold(embeddings, threshold)

        print(
            f"Próg: {result['threshold']:.2f} | "
            f"Krawędzie: {result['edges']} | "
            f"Średni stopień: {result['avg_degree']:.2f} | "
            f"Izolowane: {result['isolated']} | "
            f"Składowe: {result['components']} | "
            f"Największa składowa: {result['largest_component']}"
        )


if __name__ == "__main__":
    main()
