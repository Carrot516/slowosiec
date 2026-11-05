
import { useMemo, useState } from "react";
import "./WordBrowser.css";

type FilterMode = "all" | "available";

interface WordBrowserProps {
  words: string[];
  visibleWords: Set<string>;
  availableWords: Set<string>;
  onSelectWord: (word: string) => void;
  selectionDisabled?: boolean;
  selectionMode?: "move" | "pick";
}

const PAGE_SIZE = 80;

export default function WordBrowser({
  words,
  visibleWords,
  availableWords,
  onSelectWord,
  selectionDisabled = false,
  selectionMode = "move",
}: WordBrowserProps) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<FilterMode>("all");
  const [limit, setLimit] = useState(PAGE_SIZE);
  const picking = selectionMode === "pick";
  const sortedWords = useMemo(
    () => [...words].sort((a, b) => a.localeCompare(b, "pl")),
    [words]
  );

  const filteredWords = useMemo(() => {
    const normalizedQuery = query.trim().toLocaleLowerCase("pl-PL");

    return sortedWords.filter((word) => {
      if (
        normalizedQuery &&
        !word.toLocaleLowerCase("pl-PL").includes(normalizedQuery)
      ) {
        return false;
      }

      if (!picking && filter === "available" && !availableWords.has(word)) {
        return false;
      }

      return true;
    });
  }, [sortedWords, query, filter, availableWords, picking]);

  const displayedWords = filteredWords.slice(0, limit);

  function changeQuery(value: string) {
    setQuery(value);
    setLimit(PAGE_SIZE);
  }

  function changeFilter(value: FilterMode) {
    setFilter(value);
    setLimit(PAGE_SIZE);
  }

  return (
    <section className="word-browser">
      <div className="word-browser-header">
        <div>
          <h2>Słownik słów</h2>
          <p>
            {words.length.toLocaleString("pl-PL")} słów w grze
          </p>
        </div>

        <button
          type="button"
          onClick={() => setOpen((previous) => !previous)}
          aria-expanded={open}
        >
          {open ? "Ukryj słownik" : "Przeglądaj słowa"}
        </button>
      </div>

      {open && (
        <div className="word-browser-content">
          <input
            type="search"
            value={query}
            onChange={(event) => changeQuery(event.target.value)}
            placeholder="Wyszukaj słowo..."
            aria-label="Wyszukaj słowo w słowniku"
            autoComplete="off"
          />
          {!picking && (
            <div className="word-browser-filters">
              <button
                type="button"
                className={filter === "all" ? "active" : ""}
                aria-pressed={filter === "all"}
                onClick={() => changeFilter("all")}
              >
                Cały słownik
              </button>

              <button
                type="button"
                className={filter === "available" ? "active" : ""}
                aria-pressed={filter === "available"}
                onClick={() => changeFilter("available")}
              >
                Dostępne teraz ({availableWords.size})
              </button>
            </div>
          )}

          <p className="word-browser-count">
            Znaleziono: {filteredWords.length} słów
          </p>

          <div className="word-browser-list">
            {displayedWords.map((word) => {
              const isVisible = visibleWords.has(word);
              const isAvailable = availableWords.has(word);
              const canSelect = picking || isAvailable;

              const status = picking
                ? "Wybierz"
                : isVisible
                  ? "Na planszy"
                  : isAvailable
                    ? "Można dodać"
                    : "Niedostępne";

              return (
                <button
                  key={word}
                  type="button"
                  className={
                    "word-browser-item" +
                    (canSelect ? " available" : "")
                  }
                  disabled={!canSelect || selectionDisabled}
                  onClick={() => onSelectWord(word)}
                >
                  <span>{word}</span>
                  <span className="word-browser-status">
                    {status}
                  </span>
                </button>
              );
            })}

            {filteredWords.length === 0 && (
              <p className="word-browser-empty">
                Nie znaleziono pasujących słów.
              </p>
            )}
          </div>

          {limit < filteredWords.length && (
            <button
              type="button"
              className="word-browser-more"
              onClick={() =>
                setLimit((previous) => previous + PAGE_SIZE)
              }
            >
              Pokaż więcej
            </button>
          )}

          <p className="word-browser-help">
            {picking
                ? "Kliknij słowo, aby wybrać je do własnej rozgrywki."
                : "Kliknij dostępne słowo, aby przenieść je do pola wpisywania."}
          </p>
        </div>
      )}
    </section>

  );
}
