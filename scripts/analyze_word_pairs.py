
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

WORDS_PATH = DATA / "fasttext_words_filtered.json"
EMBEDDINGS_PATH = DATA / "embeddings_fasttext_filtered.npy"

PAIRS = [
    ("jezioro", "woda"),
    ("biblioteka", "książka"),
    ("morze", "ocean"),
    ("komputer", "laptop"),
    ("szkoła", "nauczyciel"),
    ("samochód", "droga"),
    ("kotek", "piesek"),
    ("dom", "mieszkanie"),
]

with open(WORDS_PATH, encoding="utf-8") as f:
    data = json.load(f)

words = data["words"] if isinstance(data, dict) else data
embeddings = np.load(EMBEDDINGS_PATH)

assert len(words) == len(embeddings), (
    "Liczba słów i embeddingów jest różna!"
)

word_to_index = {
    word: i for i, word in enumerate(words)
}

# Normalizacja wektorów
norms = np.linalg.norm(
    embeddings, axis=1, keepdims=True
)
vectors = embeddings / np.maximum(norms, 1e-12)

print("=== ANALIZA PAR SŁÓW ===")
print(f"Liczba słów: {len(words)}")

for word_a, word_b in PAIRS:
    print(f"\n{word_a} <-> {word_b}")

    if word_a not in word_to_index:
        print(f"  Brak słowa: {word_a}")
        continue

    if word_b not in word_to_index:
        print(f"  Brak słowa: {word_b}")
        continue

    a = word_to_index[word_a]
    b = word_to_index[word_b]

    similarity = float(vectors[a] @ vectors[b])

    similarities_a = vectors @ vectors[a]
    similarities_b = vectors @ vectors[b]

    # Ranking 1 oznacza najbliższego sąsiada,
    # z pominięciem samego słowa.
    rank_a_to_b = int(
        np.sum(similarities_a > similarity)
    )
    rank_b_to_a = int(
        np.sum(similarities_b > similarity)
    )

    # Dodajemy 1 dla czytelnego numerowania.
    rank_a_to_b = max(1, rank_a_to_b)
    rank_b_to_a = max(1, rank_b_to_a)

    print(f"  Cosine similarity: {similarity:.4f}")
    print(f"  {word_a} -> {word_b}: top {rank_a_to_b}")
    print(f"  {word_b} -> {word_a}: top {rank_b_to_a}")

    for k in [25, 40, 50, 75]:
        connected = (
            similarity >= 0.40
            and rank_a_to_b <= k
            and rank_b_to_a <= k
        )

        status = "TAK" if connected else "NIE"
        print(f"  Mutual top {k}: {status}")
