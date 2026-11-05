
import json
import re
from pathlib import Path

from wordfreq import top_n_list
from spacy.lang.pl.stop_words import STOP_WORDS

TARGET_COUNT = 10_000
CANDIDATE_COUNT = 100_000

POLISH_WORD = re.compile(r"^[a-ząćęłńóśźż]+$")


def is_valid_word(word: str) -> bool:
    return (
        3 <= len(word) <= 18
        and bool(POLISH_WORD.fullmatch(word))
        and word not in STOP_WORDS
    )


def main():
    print("Pobieranie kandydatów...")

    candidates = top_n_list(
        "pl",
        CANDIDATE_COUNT,
        wordlist="large"
    )

    words = []
    seen = set()

    for word in candidates:
        word = word.lower().strip()

        if not is_valid_word(word):
            continue

        if word in seen:
            continue

        seen.add(word)
        words.append(word)

        if len(words) >= TARGET_COUNT:
            break

    project_root = Path(__file__).resolve().parent.parent
    output_dir = project_root / "public" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "words.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(words, file, ensure_ascii=False, indent=2)

    print(f"Zapisano {len(words)} słów")
    print("Pierwsze 50 słów:")
    print(words[:50])

    print("\nOstatnie 20 słów:")
    print(words[-20:])


if __name__ == "__main__":
    main()
