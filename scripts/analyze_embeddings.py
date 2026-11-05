
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "public" / "data"

SAMPLE_SIZE = 100_000
SEED = 42

TEST_WORDS = [
    "kotek",
    "piesek",
    "samolot",
    "komputer",
    "morze",
    "szkoła",
    "miłość",
    "samochód",
]


def main():
    with (DATA_DIR / "embedding_words.json").open(
        encoding="utf-8"
    ) as f:
        words = json.load(f)

    embeddings = np.load(DATA_DIR / "embeddings.npy")

    if embeddings.shape[0] != len(words):
        raise ValueError("Liczba embeddingów nie zgadza się ze słownikiem.")

    rng = np.random.default_rng(SEED)
    n = len(words)

    print("=== KONTROLA EMBEDDINGÓW ===")
    print(f"Liczba słów: {n}")
    print(f"Wymiary: {embeddings.shape[1]}")

    norms = np.linalg.norm(embeddings, axis=1)
    print(f"Minimalna norma: {norms.min():.6f}")
    print(f"Maksymalna norma: {norms.max():.6f}")

    # Losowanie różnych indeksów słów.
    first = rng.integers(0, n, size=SAMPLE_SIZE)
    second = rng.integers(0, n, size=SAMPLE_SIZE)

    mask = first != second
    first = first[mask]
    second = second[mask]

    # Iloczyn skalarny znormalizowanych wektorów
    # jest równy podobieństwu cosinusowemu.
    similarities = np.einsum(
        "ij,ij->i",
        embeddings[first],
        embeddings[second],
    )

    print("\n=== LOSOWE PARY SŁÓW ===")
    print(f"Średnie podobieństwo: {similarities.mean():.4f}")
    print(f"Mediana: {np.median(similarities):.4f}")
    print(f"Odchylenie standardowe: {similarities.std():.4f}")

    for percentile in [1, 5, 25, 50, 75, 95, 99]:
        value = np.percentile(similarities, percentile)
        print(f"Percentyl {percentile:2d}: {value:.4f}")

    print("\n=== NAJBLIŻSI SĄSIEDZI ===")

    word_to_index = {
        word: index for index, word in enumerate(words)
    }

    for query in TEST_WORDS:
        if query not in word_to_index:
            print(f"\n{query}: BRAK W SŁOWNIKU")
            continue

        index = word_to_index[query]
        scores = embeddings @ embeddings[index]
        scores[index] = -np.inf

        top_indices = np.argsort(scores)[-10:][::-1]

        print(f"\n{query.upper()}:")

        for neighbor in top_indices:
            print(
                f"  {words[neighbor]:20} "
                f"{scores[neighbor]:.4f}"
            )


if __name__ == "__main__":
    main()
