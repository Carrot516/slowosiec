
import type { WordGraph } from "./graph";

/**
 * Zwraca długość najkrótszej ścieżki między słowami.
 * Jeśli ścieżka nie istnieje, zwraca null.
 */
export function shortestDistance(
  graph: WordGraph,
  startWord: string,
  targetWord: string
): number | null {
  const start = graph.wordToIndex.get(startWord);
  const target = graph.wordToIndex.get(targetWord);

  if (start === undefined || target === undefined) {
    return null;
  }

  if (start === target) {
    return 0;
  }

  const distances = new Int32Array(graph.words.length);
  distances.fill(-1);

  const queue: number[] = [start];
  let head = 0;

  distances[start] = 0;

  while (head < queue.length) {
    const current = queue[head++];

    for (const neighbor of graph.neighbors[current]) {
      if (distances[neighbor] !== -1) {
        continue;
      }

      distances[neighbor] = distances[current] + 1;

      if (neighbor === target) {
        return distances[neighbor];
      }

      queue.push(neighbor);
    }
  }

  return null;
}
