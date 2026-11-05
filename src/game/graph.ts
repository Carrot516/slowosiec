
export interface WordGraph {
  words: string[];
  neighbors: number[][];
  wordToIndex: Map<string, number>;
}

interface GraphFile {
  words: string[];
  neighbors: number[][];
}

function isGraphFile(value: unknown): value is GraphFile {
  if (typeof value !== "object" || value === null) {
    return false;
  }

  const record = value as Record<string, unknown>;
  const words = record.words;
  const neighbors = record.neighbors;

  if (!Array.isArray(words) || !Array.isArray(neighbors)) {
    return false;
  }

  if (words.length === 0 || words.length !== neighbors.length) {
    return false;
  }

  return (
    words.every((word: unknown) => typeof word === "string") &&
    neighbors.every(
      (row: unknown) =>
        Array.isArray(row) &&
        row.every(
          (index: unknown) =>
            typeof index === "number" &&
            Number.isInteger(index) &&
            index >= 0 &&
            index < words.length
        )
    )
  );
}

export async function loadWordGraph(): Promise<WordGraph> {
  const response = await fetch("/data/graph_fasttext_mutual.json");

  if (!response.ok) {
    throw new Error(
      `Nie udało się wczytać grafu: HTTP ${response.status}`
    );
  }

  const data: unknown = await response.json();

  if (!isGraphFile(data)) {
    throw new Error("Nieprawidłowy format pliku grafu.");
  }

  const wordToIndex = new Map<string, number>();

  data.words.forEach((word, index) => {
    wordToIndex.set(word, index);
  });

  return {
    words: data.words,
    neighbors: data.neighbors,
    wordToIndex,
  };
}

export function canConnect(
  graph: WordGraph,
  first: string,
  second: string
): boolean {
  const firstIndex = graph.wordToIndex.get(first);
  const secondIndex = graph.wordToIndex.get(second);

  if (firstIndex === undefined || secondIndex === undefined) {
    return false;
  }

  return graph.neighbors[firstIndex].includes(secondIndex);
}
