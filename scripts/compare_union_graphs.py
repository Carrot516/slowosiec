
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
EXPERIMENTS = DATA / "experiments"

WORDS_PATH = DATA / "fasttext_words_filtered.json"
EMBEDDINGS_PATH = DATA / "embeddings_fasttext_filtered.npy"

BASELINE_PATH = EXPERIMENTS / "D_mutual25_040.json"

VARIANTS = [
    ("U25_040", 25, 0.40),
    ("U50_040", 50, 0.40),
    ("U100_040", 100, 0.40),
    ("U100_035", 100, 0.35),
]

TEST_PAIRS = [
    ("jezioro", "woda"),
    ("biblioteka", "książka"),
    ("szkoła", "nauczyciel"),
    ("samochód", "droga"),
    ("morze", "ocean"),
    ("komputer", "laptop"),
    ("dom", "mieszkanie"),
]


def load_data():
    with WORDS_PATH.open(encoding="utf-8") as f:
        data = json.load(f)

    words = data["words"] if isinstance(data, dict) else data
    embeddings = np.load(EMBEDDINGS_PATH).astype(np.float32)

    with BASELINE_PATH.open(encoding="utf-8") as f:
        baseline = json.load(f)

    if words != baseline["words"]:
        raise ValueError(
            "Słowa lub ich kolejność różnią się od grafu D."
        )

    if len(words) != len(embeddings):
        raise ValueError(
            "Liczba słów i embeddingów jest różna."
        )

    return words, embeddings, baseline


def normalize(embeddings):
    norms = np.linalg.norm(
        embeddings, axis=1, keepdims=True
    )
    return embeddings / np.maximum(norms, 1e-12)


def calculate_top_neighbors(similarity, max_k):
    top_neighbors = []

    for row in similarity:
        indices = np.argpartition(
            row, -max_k
        )[-max_k:]

        indices = indices[
            np.argsort(row[indices])[::-1]
        ]

        top_neighbors.append(indices)

    return top_neighbors


def build_union_edges(similarity, top_neighbors, k, threshold):
    edges = set()

    for i, nearest in enumerate(top_neighbors):
        for j in nearest[:k]:
            j = int(j)

            if similarity[i, j] < threshold:
                continue

            a, b = min(i, j), max(i, j)
            edges.add((a, b))

    return edges


def edges_from_graph(graph):
    edges = set()

    for i, neighbors in enumerate(graph["neighbors"]):
        for j in neighbors:
            j = int(j)

            if i == j:
                continue

            edges.add((min(i, j), max(i, j)))

    return edges


def build_adjacency(number_of_words, edges):
    adjacency = [
        set() for _ in range(number_of_words)
    ]

    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)

    return adjacency


def analyze_graph(number_of_words, edges):
    adjacency = build_adjacency(number_of_words, edges)

    degrees = np.array(
        [len(row) for row in adjacency]
    )

    visited = set()
    components = []

    for start in range(number_of_words):
        if start in visited:
            continue

        stack = [start]
        visited.add(start)
        size = 0

        while stack:
            current = stack.pop()
            size += 1

            for neighbor in adjacency[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)

        components.append(size)

    return {
        "edges": len(edges),
        "avg_degree": float(np.mean(degrees)),
        "median_degree": float(np.median(degrees)),
        "isolated": int(np.sum(degrees == 0)),
        "components": len(components),
        "largest_component": max(components),
    }


def save_graph(name, words, edges):
    adjacency = build_adjacency(len(words), edges)

    graph = {
        "words": words,
        "neighbors": [
            sorted(row) for row in adjacency
        ],
    }

    output = EXPERIMENTS / f"{name}.json"

    with output.open("w", encoding="utf-8") as f:
        json.dump(
            graph,
            f,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    print(f"Zapisano: {output}")


def print_statistics(name, number_of_words, edges, baseline_edges):
    stats = analyze_graph(number_of_words, edges)

    print(f"\n=== {name} ===")
    print(f"Krawędzie: {stats['edges']}")
    print(f"Średni stopień: {stats['avg_degree']:.2f}")
    print(f"Mediana stopnia: {stats['median_degree']:.1f}")
    print(f"Izolowane słowa: {stats['isolated']}")
    print(f"Liczba składowych: {stats['components']}")
    print(
        "Największa składowa: "
        f"{stats['largest_component']} "
        f"({100 * stats['largest_component'] / number_of_words:.2f}%)"
    )

    print(
        f"Nowe krawędzie względem D: "
        f"{len(edges - baseline_edges)}"
    )


def print_test_pairs(words, results):
    index = {
        word: i for i, word in enumerate(words)
    }

    print("\n=== PORÓWNANIE WYBRANYCH PAR ===")

    for first, second in TEST_PAIRS:
        if first not in index or second not in index:
            print(f"{first} - {second}: brak w słowniku")
            continue

        a = index[first]
        b = index[second]
        edge = (min(a, b), max(a, b))

        print(f"\n{first} <-> {second}")

        for name, edges in results.items():
            connected = edge in edges

            print(
                f"  {name}: "
                f"{'TAK' if connected else 'NIE'}"
            )


def print_new_edge_examples(words, new_edges, limit=15):
    print("\nPrzykładowe nowe połączenia:")

    # Powtarzalna próbka z całego zbioru nowych krawędzi
    import random

    rng = random.Random(42)
    candidates = sorted(new_edges)
    examples = rng.sample(
        candidates,
        min(limit, len(candidates))
    )

    for a, b in examples:
        print(f"  {words[a]} <-> {words[b]}")


def main():
    EXPERIMENTS.mkdir(parents=True, exist_ok=True)

    words, embeddings, baseline = load_data()

    number_of_words = len(words)
    baseline_edges = edges_from_graph(baseline)

    print("=== PRZYGOTOWANIE ===")
    print(f"Liczba słów: {number_of_words}")

    vectors = normalize(embeddings)

    print("Obliczanie macierzy podobieństwa...")
    similarity = vectors @ vectors.T
    np.fill_diagonal(similarity, -np.inf)

    max_k = max(k for _, k, _ in VARIANTS)

    print(f"Wyznaczanie top {max_k} sąsiadów...")
    top_neighbors = calculate_top_neighbors(
        similarity, max_k
    )

    results = {"D_mutual25_040": baseline_edges}

    print_statistics(
        "D_mutual25_040",
        number_of_words,
        baseline_edges,
        baseline_edges,
    )

    for name, k, threshold in VARIANTS:
        edges = build_union_edges(
            similarity,
            top_neighbors,
            k,
            threshold,
        )

        results[name] = edges

        print_statistics(
            name,
            number_of_words,
            edges,
            baseline_edges,
        )

        print_new_edge_examples(
            words,
            edges - baseline_edges,
        )

        save_graph(name, words, edges)

    print_test_pairs(words, results)


if __name__ == "__main__":
    main()
