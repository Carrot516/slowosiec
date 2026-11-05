
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


# ---------- KONFIGURACJA ----------

MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "public" / "data"

INPUT_FILE = DATA_DIR / "words_clean.json"

OUTPUT_EMBEDDINGS = DATA_DIR / "embeddings.npy"
OUTPUT_WORDS = DATA_DIR / "embedding_words.json"
OUTPUT_METADATA = DATA_DIR / "embedding_metadata.json"

BATCH_SIZE = 32


# ---------- GENEROWANIE EMBEDDINGÓW ----------

def main():
    print("Wczytywanie słownika...")

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        words = json.load(file)

    if not isinstance(words, list) or not words:
        raise ValueError("Słownik musi być niepustą listą słów.")

    if not all(isinstance(word, str) for word in words):
        raise ValueError("Słownik zawiera nieprawidłowe dane.")

    if len(words) != len(set(words)):
        raise ValueError("Słownik zawiera duplikaty.")

    print(f"Liczba słów: {len(words)}")

    print("\nŁadowanie modelu:")
    print(MODEL_NAME)

    # Pierwsze uruchomienie pobierze model z Hugging Face.
    model = SentenceTransformer(MODEL_NAME)

    print(f"Urządzenie: {model.device}")

    print("\nGenerowanie embeddingów...")

    embeddings = model.encode(
        words,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    embeddings = np.asarray(
        embeddings,
        dtype=np.float32,
    )

    if embeddings.ndim != 2:
        raise ValueError("Nieprawidłowy wymiar embeddingów.")

    if embeddings.shape[0] != len(words):
        raise ValueError("Liczba embeddingów nie zgadza się ze słownikiem.")

    if not np.isfinite(embeddings).all():
        raise ValueError("Embeddingi zawierają NaN lub Inf.")

    print("\nKształt macierzy:")
    print(embeddings.shape)

    print("\nDługości pierwszych pięciu wektorów:")
    print(np.linalg.norm(embeddings[:5], axis=1))

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    np.save(OUTPUT_EMBEDDINGS, embeddings)

    with OUTPUT_WORDS.open("w", encoding="utf-8") as file:
        json.dump(words, file, ensure_ascii=False, indent=2)

    metadata = {
        "model": MODEL_NAME,
        "words_count": len(words),
        "embedding_dimension": int(embeddings.shape[1]),
        "normalized": True,
        "dtype": "float32",
    }

    with OUTPUT_METADATA.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, ensure_ascii=False, indent=2)

    print("\nZapisano:")
    print(OUTPUT_EMBEDDINGS)
    print(OUTPUT_WORDS)
    print(OUTPUT_METADATA)

    print("\nGotowe!")


if __name__ == "__main__":
    main()
