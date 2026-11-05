
import csv
import json
import re
from collections import Counter
from pathlib import Path

import morfeusz2
import numpy as np
from spacy.lang.pl.stop_words import STOP_WORDS
from wordfreq import zipf_frequency

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SCRIPT_DIR = Path(__file__).resolve().parent

WORDS_INPUT = DATA_DIR / "fasttext_words.json"
EMBEDDINGS_INPUT = DATA_DIR / "embeddings_fasttext.npy"

WORDS_OUTPUT = DATA_DIR / "fasttext_words_filtered.json"
EMBEDDINGS_OUTPUT = DATA_DIR / "embeddings_fasttext_filtered.npy"
REPORT_OUTPUT = DATA_DIR / "vocabulary_filter_report.csv"

EXCLUDED_PATH = SCRIPT_DIR / "excluded_words.txt"

MIN_ZIPF = 3.0
WORD_PATTERN = re.compile(r"^[a-ząćęłńóśźż]{3,18}$")

TEST_WORDS = [
    "kotek", "piesek", "samochód", "dom",
    "morze", "szkoła", "miłość", "komputer",
    "aaron", "delaware", "birkenau", "urbany",
]

morfeusz = morfeusz2.Morfeusz()


def is_noun_lemma(word):
    """Czy słowo występuje jako lemat rzeczownika?"""
    for start, end, analysis in morfeusz.analyse(word):
        if start != 0 or end != 1:
            continue

        _, lemma, tag, _, _ = analysis

        if lemma == word and tag.split(":")[0] == "subst":
            return True

    return False


def load_exclusions():
    if not EXCLUDED_PATH.exists():
        return set()

    return {
        line.strip().lower()
        for line in EXCLUDED_PATH.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def main():
    with WORDS_INPUT.open(encoding="utf-8") as f:
        words = json.load(f)

    embeddings = np.load(EMBEDDINGS_INPUT)

    if not isinstance(words, list):
        raise ValueError("Oczekiwano listy słów.")

    if embeddings.ndim != 2 or len(words) != embeddings.shape[0]:
        raise ValueError("Słowa i embeddingi mają różne rozmiary.")

    if len(set(words)) != len(words):
        raise ValueError("Słownik zawiera duplikaty.")

    # Sprawdź, czy analizujemy dokładnie obecny słownik gry.
    graph_path = ROOT / "public" / "data" / "graph_fasttext.json"

    with graph_path.open(encoding="utf-8") as f:
        current_graph = json.load(f)

    if current_graph["words"] != words:
        raise ValueError(
            "Słownik fastText różni się od słownika obecnego grafu."
        )

    excluded = load_exclusions()
    kept_indices = []
    report = []
    reasons = Counter()

    for index, word in enumerate(words):
        frequency = zipf_frequency(
            word, "pl", wordlist="large"
        )

        if word in excluded:
            reason = "manual_exclusion"
        elif (
            WORD_PATTERN.fullmatch(word) is None
            or word in STOP_WORDS
        ):
            reason = "invalid_word"
        elif not is_noun_lemma(word):
            reason = "not_noun_lemma"
        elif frequency < MIN_ZIPF:
            reason = "low_frequency"
        else:
            reason = "accepted"
            kept_indices.append(index)

        reasons[reason] += 1

        report.append({
            "word": word,
            "zipf": frequency,
            "reason": reason,
        })

    filtered_words = [words[i] for i in kept_indices]
    filtered_embeddings = embeddings[kept_indices]

    with WORDS_OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(filtered_words, f, ensure_ascii=False, indent=2)

    np.save(EMBEDDINGS_OUTPUT, filtered_embeddings)

    with REPORT_OUTPUT.open(
        "w", encoding="utf-8", newline=""
    ) as f:
        writer = csv.DictWriter(
            f, fieldnames=["word", "zipf", "reason"]
        )
        writer.writeheader()
        writer.writerows(report)

    print("\n=== FILTROWANIE SŁOWNIKA ===")
    print(f"Przed filtrowaniem: {len(words)}")
    print(f"Po filtrowaniu: {len(filtered_words)}")

    for reason, count in reasons.items():
        print(f"{reason}: {count}")

    print("\n=== KONTROLA WYBRANYCH SŁÓW ===")

    accepted = set(filtered_words)
    original = set(words)

    for word in TEST_WORDS:
        if word not in original:
            status = "nie było w słowniku"
        elif word in accepted:
            status = "zachowane"
        else:
            status = "odrzucone"

        print(f"{word:15s} {status}")

    print(f"\nRaport: {REPORT_OUTPUT}")
    print(f"Słownik: {WORDS_OUTPUT}")
    print(f"Embeddingi: {EMBEDDINGS_OUTPUT}")


if __name__ == "__main__":
    main()
