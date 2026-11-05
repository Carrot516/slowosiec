
import json
import random
from collections import Counter, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPERIMENTS = ROOT / "data" / "experiments"

GRAPHS = {
    "D_mutual25_040": EXPERIMENTS / "D_mutual25_040.json",
    "U25_040": EXPERIMENTS / "U25_040.json",
}

SAMPLE_SIZE = 150
SEED = 42


def load_graph(path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def bfs(adjacency, start):
    distances = [-1] * len(adjacency)
    distances[start] = 0

    queue = deque([start])

    while queue:
        current = queue.popleft()

        for neighbor in adjacency[current]:
            if distances[neighbor] == -1:
                distances[neighbor] = distances[current] + 1
                queue.append(neighbor)

    return distances


def largest_component(adjacency):
    visited = set()
    largest = []

    for start in range(len(adjacency)):
        if start in visited:
            continue

        component = []
        queue = deque([start])
        visited.add(start)

        while queue:
            current = queue.popleft()
            component.append(current)

            for neighbor in adjacency[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        if len(component) > len(largest):
            largest = component

    return largest


def analyze(name, graph, start_nodes, reference_nodes):
    adjacency = graph["neighbors"]
    counter = Counter()

    for start in start_nodes:
        distances = bfs(adjacency, start)

        for target in reference_nodes:
            if start == target:
                continue

            distance = distances[target]

            if distance >= 0:
                counter[distance] += 1

    total = sum(counter.values())

    average = sum(
        distance * count
        for distance, count in counter.items()
    ) / total

    short = sum(
        count for distance, count in counter.items()
        if distance <= 2
    )

    medium = sum(
        count for distance, count in counter.items()
        if 3 <= distance <= 5
    )

    long = sum(
        count for distance, count in counter.items()
        if distance >= 6
    )

    print(f"\n=== {name} ===")
    print(f"Przeanalizowanych par: {total}")
    print(f"Średnia odległość: {average:.2f}")
    print(f"Maksymalna odległość: {max(counter)}")

    print(f"Odległość 1-2: {short / total * 100:.2f}%")
    print(f"Odległość 3-5: {medium / total * 100:.2f}%")
    print(f"Odległość 6+:  {long / total * 100:.2f}%")

    print("\nRozkład odległości:")

    for distance in sorted(counter):
        percentage = counter[distance] / total * 100

        print(
            f"  {distance:2d}: "
            f"{percentage:6.2f}%"
        )


def main():
    graphs = {
        name: load_graph(path)
        for name, path in GRAPHS.items()
    }

    baseline = graphs["D_mutual25_040"]
    words = baseline["words"]

    for name, graph in graphs.items():
        if graph["words"] != words:
            raise ValueError(
                f"Niezgodność słownika w grafie {name}"
            )

    component = largest_component(
        baseline["neighbors"]
    )

    rng = random.Random(SEED)

    start_nodes = rng.sample(
        component,
        min(SAMPLE_SIZE, len(component))
    )

    print("=== PORÓWNANIE GRAFÓW ===")
    print(f"Liczba słów: {len(words)}")
    print(f"Największa składowa D: {len(component)}")
    print(f"Punktów startowych: {len(start_nodes)}")

    # Porównujemy te same pary słów w obu grafach.
    for name, graph in graphs.items():
        analyze(
            name,
            graph,
            start_nodes,
            component,
        )


if __name__ == "__main__":
    main()
