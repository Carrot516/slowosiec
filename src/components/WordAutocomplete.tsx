
import {
  useMemo,
  useState,
  type KeyboardEvent,
  type RefObject,
} from "react";

import "./WordAutocomplete.css";

interface WordAutocompleteProps {
  words: string[];
  value: string;
  onChange: (value: string) => void;
  inputRef: RefObject<HTMLInputElement | null>;
}

const MAX_SUGGESTIONS = 8;

export default function WordAutocomplete({
  words,
  value,
  onChange,
  inputRef,
}: WordAutocompleteProps) {
  const [focused, setFocused] = useState(false);
  const [highlightedIndex, setHighlightedIndex] =
    useState(-1);

  const suggestions = useMemo(() => {
    const query = value.trim().toLocaleLowerCase("pl-PL");

    if (query.length < 2) {
      return [];
    }

    return words
      .filter((word) =>
        word.toLocaleLowerCase("pl-PL").startsWith(query)
      )
      .slice(0, MAX_SUGGESTIONS);
  }, [words, value]);

  const showSuggestions =
    focused && suggestions.length > 0;

  function selectWord(word: string) {
    onChange(word);
    inputRef.current?.focus();
    setHighlightedIndex(-1);
    setFocused(false);
  }

  function handleKeyDown(
    event: KeyboardEvent<HTMLInputElement>
  ) {
    if (!showSuggestions) return;

    if (event.key === "ArrowDown") {
      event.preventDefault();

      setHighlightedIndex((previous) =>
        (previous + 1) % suggestions.length
      );
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();

      setHighlightedIndex((previous) =>
        previous <= 0
          ? suggestions.length - 1
          : previous - 1
      );
    }

    if (event.key === "Escape") {
      event.preventDefault();
      setFocused(false);
      setHighlightedIndex(-1);
    }

    if (
      event.key === "Enter" &&
      highlightedIndex >= 0
    ) {
      event.preventDefault();

      selectWord(suggestions[highlightedIndex]);
    }
  }

  return (
    <div
      className="word-autocomplete"
      onBlur={(event) => {
        if (
          !event.currentTarget.contains(
            event.relatedTarget as Node | null
          )
        ) {
          setFocused(false);
          setHighlightedIndex(-1);
        }
      }}
    >
      <input
        ref={inputRef}
        type="text"
        aria-label="Nowe słowo"
        role="combobox"
        aria-autocomplete="list"
        aria-expanded={showSuggestions}
        aria-controls="word-autocomplete-list"
        aria-activedescendant={
          showSuggestions && highlightedIndex >= 0
            ? `word-suggestion-${highlightedIndex}`
            : undefined
        }
        value={value}
        onChange={(event) => {
          onChange(event.target.value);
          setHighlightedIndex(-1);
          setFocused(true);
        }}
        onFocus={() => setFocused(true)}
        onKeyDown={handleKeyDown}
        placeholder="Wpisz skojarzenie..."
        autoComplete="off"
      />

      {showSuggestions && (
        <div
          id="word-autocomplete-list"
          className="word-autocomplete-list"
          role="listbox"
        >
          {suggestions.map((word, index) => (
            <button
              id={`word-suggestion-${index}`}
              key={word}
              type="button"
              role="option"
              aria-selected={
                highlightedIndex === index
              }
              className={
                "word-autocomplete-item" +
                (highlightedIndex === index
                  ? " highlighted"
                  : "")
              }
              onClick={() => selectWord(word)}
            >
              {word}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
