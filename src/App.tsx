import { useEffect, useRef, useState } from "react";
import {
  Background,
  Controls,
  Position,
  ReactFlow,
  useEdgesState,
  useNodesState,
  type Edge,
  type Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { canConnect, loadWordGraph, type WordGraph } from "./game/graph";
import "./App.css";
import WordBrowser from "./components/WordBrowser";
import { generateRandomPair } from "./game/randomPair";
import AboutMe from "./components/AboutMe";
import { shortestDistance } from "./game/pathfinding";
import WordAutocomplete from "./components/WordAutocomplete";
const START_WORD = "kotek";
const TARGET_WORD = "samochód";


function initialNodes(
  startWord: string,
  targetWord: string
): Node[] {
  const isMobile = window.matchMedia(
    "(max-width: 600px)"
  ).matches;

  const targetX = isMobile ? 260 : 760;

  return [
    {
      id: startWord,
      position: { x: 0, y: 100 },
      data: { label: startWord },
      className: "game-node game-node--start",
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
    },
    {
      id: targetWord,
      position: { x: targetX, y: 100 },
      data: { label: targetWord },
      className: "game-node game-node--target",
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
    },
  ];
}


function findFreePosition(parent: Node, existing: Node[]) {
  for (let column = 1; column <= 12; column++) {
    const x = parent.position.x + column * 210;
    for (let i = 0; i < 41; i++) {
      const offset = i === 0 ? 0 : Math.ceil(i / 2) * 110 * (i % 2 === 1 ? 1 : -1);
      const y = parent.position.y + offset;
      const occupied = existing.some(
        (node) =>
          Math.abs(node.position.x - x) < 170 &&
          Math.abs(node.position.y - y) < 75
      );
      if (!occupied) return { x, y };
    }
  }
  return { x: parent.position.x + 250, y: parent.position.y + 250 };
}

function generateGamePair(
  graph: WordGraph,
  previous?: { start: string; target: string }
) {
  const distanceGroup =
    Math.random() < 1 / 3 ? "easy" : "medium";

  return generateRandomPair(graph, distanceGroup, previous);
}

function App() {
  const [graph, setGraph] = useState<WordGraph | null>(null);
  const [loadError, setLoadError] = useState("");
  const [nodes, setNodes, onNodesChange] =
  useNodesState<Node>(initialNodes(START_WORD, TARGET_WORD));  const [edges, setEdges] = useEdgesState<Edge>([]);
  const [moves, setMoves] = useState<string[]>([]);
  const [input, setInput] = useState("");
  const [message, setMessage] = useState("");
  const [won, setWon] = useState(false);
  const [startWord, setStartWord] = useState(START_WORD);
  const [targetWord, setTargetWord] = useState(TARGET_WORD);
  const inputRef = useRef<HTMLInputElement>(null);
  const [showAbout, setShowAbout] = useState(false);
  const [showCustomSetup, setShowCustomSetup] = useState(false);

  const [customStart, setCustomStart] = useState("");
  const [customTarget, setCustomTarget] = useState("");

  const [pickingWord, setPickingWord] = useState<"start" | "target">("start");

  const [customError, setCustomError] = useState("");

  useEffect(() => {
    let active = true;
    loadWordGraph()
      .then((loaded) => {
        if (!active) return;
        if (!loaded.wordToIndex.has(START_WORD) || !loaded.wordToIndex.has(TARGET_WORD)) {
          setLoadError("Brakuje słowa początkowego lub docelowego w grafie.");
          return;
        }
        const pair = generateGamePair(loaded);

        setStartWord(pair.start);
        setTargetWord(pair.target);
        setNodes(initialNodes(pair.start, pair.target));
        setGraph(loaded);
      })
      .catch((error: unknown) => {
        if (!active) return;
        setLoadError(error instanceof Error ? error.message : "Błąd odczytu grafu.");
      });
    return () => { active = false; };
  }, []);

  function addWord() {
    if (!graph || won) return;
    const word = input.trim().toLocaleLowerCase("pl-PL");
    if (!word) return;
    if (!graph.wordToIndex.has(word)) {
      setMessage(`Słowa „${word}” nie ma w słowniku.`);
      return;
    }
    if (word === targetWord) {
      setMessage("Cel połączy się automatycznie, gdy odkryjesz jego sąsiada.");
      return;
    }
    if (nodes.some((node) => node.id === word)) {
      setMessage("To słowo jest już na planszy.");
      return;
    }

    const connected = nodes.filter(
      (node) => node.id !== targetWord && canConnect(graph, node.id, word)
    );
    if (connected.length === 0) {
      setMessage("To słowo nie łączy się z żadnym odkrytym słowem.");
      return;
    }

    const position = findFreePosition(connected[0], nodes);
    const newNode: Node = {
      id: word,
      position,
      data: { label: word },
      className: "game-node game-node--normal",
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
    };
    const newEdges: Edge[] = connected.map((node) => ({
      id: `${node.id}:${word}`,
      source: node.id,
      target: word,
      type: "smoothstep",
    }));
    const reachesTarget = canConnect(graph, word, targetWord);
    if (reachesTarget) {
      newEdges.push({
        id: `${word}:${targetWord}`,
        source: word,
        target: targetWord,
        type: "smoothstep",
        animated: true,
      });
    }

    setNodes((previous) => [...previous, newNode]);
    setEdges((previous) => [...previous, ...newEdges]);
    setMoves((previous) => [...previous, word]);
    setWon(reachesTarget);
    setInput("");
    setMessage("");
  }

  function openCustomSetup() {
    setCustomStart(startWord);
    setCustomTarget(targetWord);
    setPickingWord("start");
    setCustomError("");
    setShowCustomSetup(true);
  }


  function startCustomGame() {
    if (!graph) return;

    const first = customStart.trim().toLocaleLowerCase("pl-PL");
    const second = customTarget.trim().toLocaleLowerCase("pl-PL");

    if (!first || !second) {
      setCustomError("Wybierz oba słowa.");
      return;
    }

    if (!graph.wordToIndex.has(first)) {
      setCustomError(`Słowa „${first}” nie ma w słowniku.`);
      return;
    }

    if (!graph.wordToIndex.has(second)) {
      setCustomError(`Słowa „${second}” nie ma w słowniku.`);
      return;
    }

    if (first === second) {
      setCustomError("Wybierz dwa różne słowa.");
      return;
    }

    const distance = shortestDistance(graph, first, second);

    if (distance === null) {
      setCustomError(
        "Nie istnieje ścieżka między tymi słowami. Wybierz inną parę."
      );
      return;
    }

    if (distance === 1) {
      setCustomError(
        "Te słowa są już bezpośrednio połączone. Wybierz trudniejszą parę."
      );
      return;
    }

    setStartWord(first);
    setTargetWord(second);

    setNodes(initialNodes(first, second));
    setEdges([]);
    setMoves([]);

    setInput("");
    setMessage("");
    setWon(false);

    setCustomError("");
    setShowCustomSetup(false);
  }


  function undoMove() {
    const last = moves[moves.length - 1];
    if (!last) return;
    setNodes((previous) => previous.filter((node) => node.id !== last));
    setEdges((previous) => previous.filter((edge) => edge.source !== last && edge.target !== last));
    setMoves((previous) => previous.slice(0, -1));
    setWon(false);
    setMessage("");
    setInput("");
  }

  function resetGame() {
    setNodes(initialNodes(startWord, targetWord));
    setEdges([]);
    setMoves([]);
    setInput("");
    setMessage("");
    setWon(false);
  }

  function newGame() {
    if (!graph) return;

    try {
      const pair = generateGamePair(graph, {
        start: startWord,
        target: targetWord,
      });

      setStartWord(pair.start);
      setTargetWord(pair.target);
      setNodes(initialNodes(pair.start, pair.target));
      setEdges([]);
      setMoves([]);
      setInput("");
      setMessage("");
      setWon(false);
      setShowCustomSetup(false);
      setCustomError("");
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "Nie udało się wylosować nowej gry."
      );
    }
  }

  const visibleWords = new Set(nodes.map((node) => node.id));
  const possible = new Set<string>();
  if (graph) {
    for (const node of nodes) {
      if (node.id === targetWord) continue;
      const index = graph.wordToIndex.get(node.id);
      if (index === undefined) continue;
      for (const neighborIndex of graph.neighbors[index]) {
        const neighbor = graph.words[neighborIndex];
        if (!visibleWords.has(neighbor)) possible.add(neighbor);
      }
    }
  }

  if (loadError) return <main className="game"><h1>Słowosieć</h1><p role="alert">{loadError}</p></main>;
  if (!graph) return <main className="game"><h1>Słowosieć</h1><p>Wczytywanie grafu...</p></main>;

  return (
      <main className="game">
        <header className="game-header">
          <div>
            <h1>Słowosieć</h1>
            <p>
              Zacznij od zielonego słowa{" "}
              <strong>{startWord}</strong> po lewej stronie.
              Dodawaj skojarzenia, aby dotrzeć do żółtego
              słowa <strong>{targetWord}</strong> po prawej.
            </p>
          </div>

          <div className="game-header-actions">
            <div className="game-stats">
              Ruchy: <strong>{moves.length}</strong>
            </div>

            <button
                type="button"
                className="about-toggle"
                onClick={() => setShowAbout((previous) => !previous)}
                aria-expanded={showAbout}
                aria-controls="about-me"
            >
              {showAbout ? "Zamknij" : "O mnie"}
            </button>
          </div>
        </header>
        {showAbout && (
            <AboutMe onClose={() => setShowAbout(false)}/>
        )}

        <div className="graph-canvas">
          <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              nodesConnectable={false}
              deleteKeyCode={null}
              fitView
              fitViewOptions={{
                padding: 0.12,
                minZoom: 0.2,
                maxZoom: 1,
              }}
              preventScrolling={false}
              zoomOnScroll={false}
              key={`${startWord}-${targetWord}`}
          >
            <Background gap={20} size={1}/>
            <Controls/>
          </ReactFlow>
        </div>
        <p className="game-caption">Przeciągaj słowa, przesuwaj planszę i przybliżaj widok. Przycisk w lewym dolnym rogu
          dopasowuje cały graf.</p>

        {won ? (
            <p className="win-message" role="status">Wygrana! Połączyłeś oba słowa w {moves.length} ruchach.</p>
        ) : (

            <form
                className="word-form"
                onSubmit={(event) => {
                  event.preventDefault();
                  addWord();
                }}
            >
              <WordAutocomplete
                  words={graph.words}
                  value={input}
                  onChange={setInput}
                  inputRef={inputRef}
              />

              <button type="submit">
                Dodaj słowo
              </button>
            </form>

        )}
        <p className="game-message" role="status">{message}</p>

        <div className="game-controls">


          <div className="game-control-group">
            <h3>Nowa rozgrywka</h3>

            <div className="game-actions">
              <button
                  type="button"
                  className="primary-action"
                  onClick={newGame}
              >
                Losuj nowe słowa
              </button>

              <button
                  type="button"
                  onClick={openCustomSetup}
              >
                Własna gra
              </button>
            </div>
          </div>


          <div className="game-control-group">
            <h3>Aktualna rozgrywka</h3>

            <div className="game-actions">
              <button
                  type="button"
                  onClick={undoMove}
                  disabled={moves.length === 0}
              >
                Cofnij ruch
              </button>

              <button
                  type="button"
                  onClick={resetGame}
              >
                Spróbuj ponownie
              </button>
            </div>
          </div>

        </div>

        {showCustomSetup && (
            <section className="custom-game">
              <h2>Własna rozgrywka</h2>

              <p>
                Wybierz dwa słowa. Możesz wpisać je ręcznie
                albo kliknąć odpowiednie słowo w słowniku poniżej.
              </p>

              <div className="custom-game-fields">
                <label>
                  Słowo początkowe
                  <input
                      type="text"
                      value={customStart}
                      onChange={(event) => {
                        setCustomStart(event.target.value);
                        setCustomError("");
                      }}
                      onFocus={() => setPickingWord("start")}
                      placeholder="Pierwsze słowo"
                  />
                </label>

                <label>
                  Słowo docelowe
                  <input
                      type="text"
                      value={customTarget}
                      onChange={(event) => {
                        setCustomTarget(event.target.value);
                        setCustomError("");
                      }}
                      onFocus={() => setPickingWord("target")}
                      placeholder="Drugie słowo"
                  />
                </label>
              </div>

              <div className="custom-game-actions">
                <button
                    type="button"
                    className={pickingWord === "start" ? "selected" : ""}
                    aria-pressed={pickingWord === "start"}
                    onClick={() => setPickingWord("start")}
                >
                  Wybierz początek z listy
                </button>

                <button
                    type="button"
                    className={pickingWord === "target" ? "selected" : ""}
                    aria-pressed={pickingWord === "target"}
                    onClick={() => setPickingWord("target")}
                >
                  Wybierz cel z listy
                </button>
              </div>

              {customError && (
                  <p className="game-message" role="alert">
                    {customError}
                  </p>
              )}

              <div className="custom-game-actions">
                <button
                    type="button"
                    className="custom-game-start"
                    onClick={startCustomGame}
                >
                  Rozpocznij grę
                </button>

                <button
                    type="button"
                    onClick={() => {
                      setShowCustomSetup(false);
                      setCustomError("");
                    }}
                >
                  Anuluj
                </button>
              </div>
            </section>
        )}


        <WordBrowser
            words={graph.words}
            visibleWords={visibleWords}
            availableWords={possible}
            selectionMode={showCustomSetup ? "pick" : "move"}
            selectionDisabled={!showCustomSetup && won}
            onSelectWord={(word) => {
              if (showCustomSetup) {
                if (pickingWord === "start") {
                  setCustomStart(word);
                  setPickingWord("target");
                } else {
                  setCustomTarget(word);
                }

                setCustomError("");
                return;
              }

              setInput(word);
              inputRef.current?.focus();
            }}
        />
        <footer className="game-footer">
          <p>
            Słowosieć to niezależny projekt inspirowany grą{" "}
            <a
                href="https://linxicon.com/"
                target="_blank"
                rel="noopener noreferrer"
            >
              Linxicon
            </a>.
          </p>

          <p>
            Stworzono z myślą o konferencji Elements na AGH.
          </p>
        </footer>
      </main>

  );
}

export default App;
