
import type { WordGraph } from "./graph";

export type Difficulty = "easy" | "medium" | "hard";

export interface WordPair {
  start: string;
  target: string;
  distance: number;
}

const WORD_POOL = [
  "kotek", "piesek", "zwierzak", "samochód", "dom",
  "morze", "szkoła", "miłość", "komputer", "ocean",
  "jezioro", "słońce", "niebo", "plaża", "wakacje",
  "samolot", "statek", "autobus", "laptop", "tablet",
  "telefon", "telewizor", "internet", "serwer",
  "przyjaźń", "radość", "samotność", "wiara",
  "człowiek", "dziecko", "rodzina", "kobieta",
  "mężczyzna", "chłopiec", "dziewczynka",
  "nauczyciel", "lekarz", "szpital", "książka",
  "biblioteka", "film", "obraz", "muzyka", "kino",
  "teatr", "las", "drzewo", "kwiat", "kawa",
  "herbata", "chleb", "woda", "deszcz", "śnieg",
  "wiatr", "burza", "rower", "pociąg", "droga",
  "miasto", "wieś", "kraj", "świat", "historia",
  "nauka", "wiedza", "praca", "pieniądze", "bank",
  "czas", "życie", "zdrowie", "sport", "mecz",
  "ogród", "pokój", "mieszkanie", "kuchnia",
  "stół", "krzesło", "okno", "drzwi", "klucz",
  "twarz", "ręka", "głowa", "serce", "pamięć",
  "sen", "marzenie", "strach", "przyszłość",
];

const DISTANCES: Record<Difficulty, number[]> = {
  easy: [3],
  medium: [4, 5],
  hard: [6, 7],
};

function shuffle<T>(items: T[]): T[] {
  const result = [...items];

  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }

  return result;
}

function largestComponent(graph: WordGraph): Set<number> {
  const visited = new Uint8Array(graph.words.length);
  let largest: number[] = [];

  for (let start = 0; start < graph.words.length; start++) {
    if (visited[start]) continue;

    const component: number[] = [];
    const queue = [start];
    let head = 0;
    visited[start] = 1;

    while (head < queue.length) {
      const current = queue[head++];
      component.push(current);

      for (const next of graph.neighbors[current]) {
        if (visited[next]) continue;
        visited[next] = 1;
        queue.push(next);
      }
    }

    if (component.length > largest.length) {
      largest = component;
    }
  }

  return new Set(largest);
}

function bfsDistances(
  graph: WordGraph,
  start: number,
  maxDistance: number
): Int16Array {
  const distances = new Int16Array(graph.words.length);
  distances.fill(-1);

  const queue = [start];
  let head = 0;
  distances[start] = 0;

  while (head < queue.length) {
    const current = queue[head++];
    const distance = distances[current];

    if (distance >= maxDistance) continue;

    for (const next of graph.neighbors[current]) {
      if (distances[next] !== -1) continue;

      distances[next] = distance + 1;
      queue.push(next);
    }
  }

  return distances;
}

export function generateRandomPair(
  graph: WordGraph,
  difficulty: Difficulty,
  previous?: { start: string; target: string }
): WordPair {
  const allowedDistances = DISTANCES[difficulty];
  const maxDistance = Math.max(...allowedDistances);
  const component = largestComponent(graph);

  const endpoints = [
    ...new Set(
      WORD_POOL
        .map((word) => graph.wordToIndex.get(word))
        .filter(
          (index): index is number =>
            index !== undefined && component.has(index)
        )
    ),
  ];

  // Losujemy kolejność startów, aby nie faworyzować
  // pierwszych słów z WORD_POOL.
  for (const startIndex of shuffle(endpoints)) {
    const distances = bfsDistances(
      graph,
      startIndex,
      maxDistance
    );

    const candidates = endpoints.filter((targetIndex) => {
      const distance = distances[targetIndex];

      if (!allowedDistances.includes(distance)) {
        return false;
      }

      const start = graph.words[startIndex];
      const target = graph.words[targetIndex];

      // Nie powtarzamy ostatniej pary, również odwróconej.
      if (
        previous &&
        (
          (previous.start === start && previous.target === target) ||
          (previous.start === target && previous.target === start)
        )
      ) {
        return false;
      }

      return true;
    });

    if (candidates.length > 0) {
      const targetIndex =
        candidates[Math.floor(Math.random() * candidates.length)];

      return {
        start: graph.words[startIndex],
        target: graph.words[targetIndex],
        distance: distances[targetIndex],
      };
    }
  }

  throw new Error(
    "Brak dostępnych par dla tego poziomu trudności."
  );
}
