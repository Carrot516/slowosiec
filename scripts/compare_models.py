
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent.parent

MINILM_DIR = ROOT / "public" / "data"
FASTTEXT_DIR = ROOT / "data"

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

TOP_K = 10


def load_model_data(words_path, embeddings_path):
    with words_path.open(encoding="utf-8") as file:
        words = json.load(file)

    embeddings = np.load(embeddings_path)

    if len(words) != len(embeddings):
        raise ValueError("Niezgodność słów i embeddingów.")

    return words, embeddings


def nearest_neighbors(query, words, embeddings, k=10):
    word_to_index = {
        word: index
        for index, word in enumerate(words)
    }

    if query not in word_to_index:
        return []

    index = word_to_index[query]

    similarities = embeddings @ embeddings[index]
    similarities[index] = -np.inf

    top_indices = np.argsort(similarities)[-k:][::-1]

    return [
        (words[i], float(similarities[i]))
        for i in top_indices
    ]


def main():
    mini_words, mini_vectors = load_model_data(
        MINILM_DIR / "embedding_words.json",
        MINILM_DIR / "embeddings.npy",
    )

    fast_words, fast_vectors = load_model_data(
        FASTTEXT_DIR / "fasttext_words.json",
        FASTTEXT_DIR / "embeddings_fasttext.npy",
    )

    if mini_words != fast_words:
        raise ValueError(
            "Modele mają różne słowniki lub kolejność słów!"
        )

    print("=== PORÓWNANIE MODELI ===")
    print(f"Liczba słów: {len(mini_words)}")
    print(f"MiniLM: {mini_vectors.shape}")
    print(f"fastText: {fast_vectors.shape}")

    for word in TEST_WORDS:
        print(f"\n{'=' * 50}")
        print(f"SŁOWO: {word.upper()}")
        print(f"{'=' * 50}")

        mini_results = nearest_neighbors(
            word, mini_words, mini_vectors, TOP_K
        )

        fast_results = nearest_neighbors(
            word, fast_words, fast_vectors, TOP_K
        )

        if not mini_results:
            print("Słowa nie ma w słowniku.")
            continue

        print(f"{'MiniLM':28} fastText")
        print("-" * 60)

        for i in range(TOP_K):
            m_word, m_score = mini_results[i]
            f_word, f_score = fast_results[i]

            print(
                f"{m_word:17} {m_score:.4f}   "
                f"{f_word:17} {f_score:.4f}"
            )


if __name__ == "__main__":
    main()
