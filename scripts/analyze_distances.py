
import json
import random
from collections import Counter, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRAPH_PATH = (
    ROOT / "data" / "experiments" / "D_mutual25_040.json"
)
SAMPLE_SIZE = 200
SEED = 42


def largest_connected_component(neighbors):
    """Zwraca wierzchołki największej spójnej składowej."""
    n = len(neighbors)
    visited = bytearray(n)
    largest = []

    for start in range(n):
        if visited[start]:
            continue

        component = []
        queue = deque([start])
        visited[start] = 1

        while queue:
            vertex = queue.popleft()
            component.append(vertex)

            for neighbor in neighbors[vertex]:
                if not visited[neighbor]:
                    visited[neighbor] = 1
                    queue.append(neighbor)

        if len(component) > len(largest):
            largest = component

    return largest


def bfs(start, neighbors):
    """Oblicza najkrótsze odległości i poprzedników."""
    n = len(neighbors)
    distances = [-1] * n
    parents = [-1] * n

    distances[start] = 0
    queue = deque([start])

    while queue:
        vertex = queue.popleft()

        for neighbor in neighbors[vertex]:
            if distances[neighbor] != -1:
                continue

            distances[neighbor] = distances[vertex] + 1
            parents[neighbor] = vertex
            queue.append(neighbor)

    return distances, parents


def reconstruct_path(start, target, parents):
    """Odtwarza jedną z najkrótszych ścieżek."""
    path = []
    current = target

    while current != -1:
        path.append(current)

        if current == start:
            return path[::-1]

        current = parents[current]

    return []


def main():
    with GRAPH_PATH.open(encoding="utf-8") as file:
        graph = json.load(file)

    words = graph["words"]
    neighbors = graph["neighbors"]

    if len(words) != len(neighbors):
        raise ValueError("Niezgodna liczba słów i list sąsiedztwa.")

    rng = random.Random(SEED)

    component = largest_connected_component(neighbors)
    sample_size = min(SAMPLE_SIZE, len(component))
    starts = rng.sample(component, sample_size)

    distance_counts = Counter()
    examples = {}

    print("=== ANALIZA ODLEGŁOŚCI W GRAFIE ===")
    print(f"Liczba wszystkich słów: {len(words)}")
    print(f"Największa składowa: {len(component)}")
    print(f"Liczba wylosowanych punktów startowych: {sample_size}")

    for number, start in enumerate(starts, 1):
        distances, parents = bfs(start, neighbors)

        # Pary o odległości 0 i 1 pomijamy:
        # nie wymagają dodania słowa pośredniego.
        grouped = {}

        for target in component:
            distance = distances[target]

            if distance < 2:
                continue

            distance_counts[distance] += 1

            # Przykładowe cele zbieramy tylko dla
            # pierwszych 10 wylosowanych startów.
            if number <= 10:
                grouped.setdefault(distance, []).append(target)

        if number <= 10:
            for distance, candidates in grouped.items():
                target = rng.choice(candidates)
                path = reconstruct_path(start, target, parents)
                examples[distance] = path

        if number % 25 == 0 or number == sample_size:
            print(f"Przeanalizowano {number}/{sample_size} słów")

    total = sum(distance_counts.values())

    if total == 0:
        print("Nie znaleziono par wymagających ruchu.")
        return

    print("\n=== ROZKŁAD ODLEGŁOŚCI ===")

    cumulative = 0
    median_distance = None

    for distance in sorted(distance_counts):
        count = distance_counts[distance]
        percent = 100 * count / total
        cumulative += count

        if median_distance is None and cumulative >= total / 2:
            median_distance = distance

        bar = "#" * round(percent / 2)

        print(
            f"Odległość {distance:2d} | "
            f"{count:9d} par | "
            f"{percent:6.2f}% | {bar}"
        )

    mean_distance = sum(
        distance * count
        for distance, count in distance_counts.items()
    ) / total

    print("\n=== PODSUMOWANIE ===")
    print(f"Liczba zbadanych par: {total}")
    print(f"Średnia odległość: {mean_distance:.2f}")
    print(f"Mediana odległości: {median_distance}")
    print(f"Maksymalna zaobserwowana odległość: {max(distance_counts)}")

    print("\n=== PRZYKŁADOWE NAJKRÓTSZE ŚCIEŻKI ===")

    for distance in sorted(examples):
        path = examples[distance]
        names = [words[index] for index in path]

        print(
            f"Odległość {distance} "
            f"({distance - 1} ruchów): "
            + " -> ".join(names)
        )


if __name__ == "__main__":
    main()
