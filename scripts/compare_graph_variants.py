
import json
import random
from collections import deque
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUTPUT = DATA / "experiments"

CONFIGS = [
    ("D_mutual25_040", 25, 0.40, True),
    ("G_mutual25_043", 25, 0.43, True),
    ("H_mutual25_045", 25, 0.45, True),
    ("I_mutual25_047", 25, 0.47, True),
    ("E_mutual25_050", 25, 0.50, True),
]

TEST_EDGES = [
    ("warszawa", "klimatyzacja"),
    ("szpital", "bankomat"),
    ("jaszczurka", "pantera"),
    ("chłopiec", "chłopczyk"),
    ("kotek", "piesek"),
    ("komputer", "laptop"),
    ("morze", "statek"),
]

TEST_PATHS = [
    ("kotek", "samochód"),
    ("morze", "samolot"),
    ("komputer", "szkoła"),
    ("dom", "miłość"),
]


def calculate_top_neighbors(embeddings, k=25):
    n = len(embeddings)
    result = []

    for start in range(0, n, 256):
        end = min(start + 256, n)
        similarities = embeddings[start:end] @ embeddings.T

        rows = np.arange(end - start)
        similarities[rows, np.arange(start, end)] = -np.inf

        indices = np.argpartition(
            similarities, -k, axis=1
        )[:, -k:]

        scores = np.take_along_axis(
            similarities, indices, axis=1
        )

        order = np.argsort(-scores, axis=1)

        indices = np.take_along_axis(indices, order, axis=1)
        scores = np.take_along_axis(scores, order, axis=1)

        for row_indices, row_scores in zip(indices, scores):
            result.append([
                (int(j), float(s))
                for j, s in zip(row_indices, row_scores)
            ])

    return result


def build_graph(top_neighbors, k, threshold, mutual):
    n = len(top_neighbors)
    selected = [
        {
            j for j, score in row[:k]
            if score >= threshold
        }
        for row in top_neighbors
    ]

    neighbors = [set() for _ in range(n)]

    for i, candidates in enumerate(selected):
        for j in candidates:
            if mutual and i not in selected[j]:
                continue

            neighbors[i].add(j)
            neighbors[j].add(i)

    return [sorted(row) for row in neighbors]


def component_sizes(neighbors):
    visited = set()
    sizes = []

    for start in range(len(neighbors)):
        if start in visited:
            continue

        queue = deque([start])
        visited.add(start)
        size = 0

        while queue:
            current = queue.popleft()
            size += 1

            for neighbor in neighbors[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        sizes.append(size)

    return sizes


def shortest_path(start, target, neighbors):
    queue = deque([start])
    parents = {start: None}

    while queue:
        current = queue.popleft()

        if current == target:
            path = []

            while current is not None:
                path.append(current)
                current = parents[current]

            return path[::-1]

        for neighbor in neighbors[current]:
            if neighbor not in parents:
                parents[neighbor] = current
                queue.append(neighbor)

    return None


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)

    with (DATA / "fasttext_words_filtered.json").open(
        encoding="utf-8"
    ) as file:
        words = json.load(file)

    embeddings = np.load(
        DATA / "embeddings_fasttext_filtered.npy"
    ).astype(np.float32)

    if embeddings.ndim != 2 or len(words) != len(embeddings):
        raise ValueError("Niezgodna liczba słów i embeddingów.")

    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)

    if not np.isfinite(embeddings).all() or np.any(norms < 1e-12):
        raise ValueError("Nieprawidłowe embeddingi.")

    embeddings = np.ascontiguousarray(embeddings / norms)
    word_to_id = {word: i for i, word in enumerate(words)}

    print("Wyznaczanie najbliższych sąsiadów...")
    top_neighbors = calculate_top_neighbors(embeddings)

    for name, k, threshold, mutual in CONFIGS:
        neighbors = build_graph(
            top_neighbors, k, threshold, mutual
        )

        degrees = [len(row) for row in neighbors]
        sizes = component_sizes(neighbors)

        print(f"\n{'=' * 55}")
        print(f"WARIANT: {name}")
        print(f"Krawędzie: {sum(degrees) // 2}")
        print(f"Średni stopień: {np.mean(degrees):.2f}")
        print(f"Izolowane: {sum(d == 0 for d in degrees)}")
        print(f"Liczba składowych: {len(sizes)}")
        print(f"Największa składowa: {max(sizes)}")

        print("\nKontrola wybranych krawędzi:")

        for first, second in TEST_EDGES:
            if first not in word_to_id or second not in word_to_id:
                continue

            i = word_to_id[first]
            j = word_to_id[second]

            similarity = float(embeddings[i] @ embeddings[j])
            exists = j in neighbors[i]

            print(
                f"  {first} <-> {second}: "
                f"{'TAK' if exists else 'NIE'} "
                f"(sim={similarity:.3f})"
            )

        print("\nPrzykładowe ścieżki:")

        for first, second in TEST_PATHS:
            if first not in word_to_id or second not in word_to_id:
                continue

            path = shortest_path(
                word_to_id[first],
                word_to_id[second],
                neighbors
            )

            print(
                f"  {first} -> {second}: "
                + (
                    " -> ".join(words[i] for i in path)
                    if path else "BRAK ŚCIEŻKI"
                )
            )

        edges = [
            (i, j)
            for i, row in enumerate(neighbors)
            for j in row
            if i < j
        ]

        rng = random.Random(42)
        print("\n10 losowych krawędzi:")

        for i, j in rng.sample(edges, min(10, len(edges))):
            print(f"  {words[i]} <-> {words[j]}")

        output_path = OUTPUT / f"{name}.json"

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(
                {"words": words, "neighbors": neighbors},
                file,
                ensure_ascii=False,
                separators=(",", ":")
            )

        print(f"\nZapisano: {output_path.name}")


if __name__ == "__main__":
    main()
