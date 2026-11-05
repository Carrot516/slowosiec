
import json
from pathlib import Path

import fasttext
import numpy as np


ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = ROOT / "models" / "cc.pl.300.bin"
WORDS_PATH = ROOT / "public" / "data" / "embedding_words.json"

# Dane eksperymentalne poza folderem public.
OUTPUT_DIR = ROOT / "data"
OUTPUT_EMBEDDINGS = OUTPUT_DIR / "embeddings_fasttext.npy"
OUTPUT_WORDS = OUTPUT_DIR / "fasttext_words.json"


def main():
    print("Wczytywanie słownika...")

    with WORDS_PATH.open(encoding="utf-8") as file:
        words = json.load(file)

    if not isinstance(words, list) or not words:
        raise ValueError("Nieprawidłowy słownik.")

    print(f"Liczba słów: {len(words)}")

    print("\nŁadowanie modelu fastText...")
    model = fasttext.load_model(str(MODEL_PATH))

    dimension = model.get_dimension()
    print(f"Wymiary embeddingów: {dimension}")

    embeddings = np.empty(
        (len(words), dimension),
        dtype=np.float32,
    )

    out_of_vocabulary = 0

    print("\nGenerowanie embeddingów...")

    for index, word in enumerate(words):
        vector = model.get_word_vector(word)

        norm = np.linalg.norm(vector)

        if not np.isfinite(norm) or norm < 1e-12:
            raise ValueError(
                f"Nieprawidłowy embedding: {word}"
            )

        embeddings[index] = vector / norm

        if model.get_word_id(word) < 0:
            out_of_vocabulary += 1

        if (index + 1) % 1000 == 0:
            print(f"Przetworzono {index + 1}/{len(words)}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    np.save(OUTPUT_EMBEDDINGS, embeddings)

    with OUTPUT_WORDS.open("w", encoding="utf-8") as file:
        json.dump(words, file, ensure_ascii=False, indent=2)

    print("\n=== PODSUMOWANIE ===")
    print(f"Kształt macierzy: {embeddings.shape}")
    print(f"Słowa spoza słownika modelu: {out_of_vocabulary}")
    print(f"Minimalna norma: {np.linalg.norm(embeddings, axis=1).min():.4f}")
    print(f"Maksymalna norma: {np.linalg.norm(embeddings, axis=1).max():.4f}")

    print("\nZapisano:")
    print(OUTPUT_EMBEDDINGS)
    print(OUTPUT_WORDS)


if __name__ == "__main__":
    main()
