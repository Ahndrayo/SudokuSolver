# SudokuSolver Handoff

## 1. Repository overview

The project is a Python Sudoku solver with a Streamlit frontend.

Important files:

- `app.py` — Streamlit application and UI state management.
- `solver.py` — reusable DOcplex/CPLEX Sudoku solver.
- `validation.py` — validates grids and identifies conflicting cells.
- `puzzles.py` — loads and queries catalogue puzzles.
- `puzzles.json` — puzzle catalogue containing IDs, names, difficulty labels, and clue grids.
- `sudoku_component.py` — Python wrapper for the custom Streamlit grid component.
- `sudoku_component/index.html` — interactive Sudoku board UI, keyboard navigation, buttons, styling, and browser-to-Python communication.
- `main.ipynb` — original notebook experiment. The deployed app uses `solver.py`, not the notebook directly.
- `tests/test_solver.py` — solver tests.
- `tests/test_puzzles.py` — catalogue tests.
- `README.md` — setup and usage instructions.
- `requirements.txt` — project dependencies.

The linked repository should be treated as the source of truth for the final code.

## 2. How to run

Language:

- Python 3.10.11

The project uses:

- Streamlit 1.65.0
- DOcplex 2.32.264
- IBM CPLEX 22.2.0.1
- pytest for tests

Activate the existing Windows virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies if necessary:

```powershell
python -m pip install -r requirements.txt
```

Run the app:

```powershell
python -m streamlit run app.py
```

Run tests:

```powershell
python -m pytest -q
```

The solver requires the CPLEX runtime. If CPLEX is unavailable, `solver.py` will not be able to solve puzzles.

## 3. Code structure

### Grid representation

At the application level, grids are represented as 9x9 nested lists:

```python
[
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    ...
]
```

- Values `1` through `9` represent numbers.
- `0` represents an empty cell.

Catalogue grids are stored in `puzzles.json` as nine-character strings, for example:

```json
"530070000"
```

`puzzles.py` converts these into immutable tuples of tuples inside a `Puzzle` dataclass.

### Main classes

`solver.py`:

```python
class SudokuSolveError(ValueError)
```

Raised for invalid puzzles or puzzles with no feasible solution.

`puzzles.py`:

```python
@dataclass(frozen=True)
class Puzzle:
    id: str
    name: str
    difficulty: str
    grid: tuple[tuple[int, ...], ...]
```

### Important functions

`solver.py`:

```python
solve_sudoku(grid) -> list[list[int]]
```

This is the solver’s public entry point. It validates the input, builds a fresh optimization model, solves it, and returns a completed 9x9 grid.

`validation.py`:

```python
validate_grid(grid) -> list[str]
conflicting_cells(grid) -> list[tuple[int, int]]
```

`puzzles.py`:

```python
get_puzzles()
get_puzzle(puzzle_id)
get_puzzles_by_difficulty(difficulty)
available_difficulties()
```

`app.py`:

- `_initialise_state()` — initializes Streamlit session state.
- `_set_puzzle()` — loads a catalogue puzzle into play mode.
- `_set_next_puzzle()` — cycles to the next puzzle at the selected difficulty.
- `_reset_answers()` — clears player answers.
- `_enter_custom_mode()` — switches to custom puzzle setup.
- `_evaluate_answers()` — compares player entries against the solver’s solution.
- `main()` — renders the app and handles component actions.

The custom HTML component returns action dictionaries such as:

```python
{"action": "check", "grid": [...]}
{"action": "new_puzzle", "grid": [...]}
{"action": "difficulty", "difficulty": "Hard", "grid": [...]}
```

Streamlit reruns `main()` after an interaction, and `st.session_state` preserves the application state.

## 4. Solver algorithm

The solver uses mixed-integer linear programming through DOcplex and IBM CPLEX.

It creates:

- `x[row, column]` — integer variables from 1 to 9.
- `p[row, column, value]` — binary one-hot variables indicating whether a value is present in a cell.

Constraints enforce:

1. Every value appears exactly once in each row.
2. Every value appears exactly once in each column.
3. Every value appears exactly once in each 3x3 box.
4. Each cell contains exactly one value.
5. Each `x` variable equals the weighted sum of its one-hot `p` variables.
6. Given clues are fixed with constraints such as:

```python
x[row, column] == clue_value
```

The solver does not use traditional backtracking or explicit constraint propagation.

Optimizations and design choices:

- The grid is validated before model construction.
- A fresh model is created for every solve, keeping calls independent.
- Duplicate clues and out-of-range values are rejected early.
- The model returns one feasible solution.

## 5. Improvements made

- Extracted the notebook solver logic into reusable `solver.py`.
- Added validation helpers in `validation.py`.
- Replaced the original hardcoded frontend puzzle with a catalogue.
- Added `puzzles.json` for data-driven puzzle storage.
- Added puzzle IDs, names, and difficulty labels.
- Added Easy, Medium, Hard, and Expert difficulty selection.
- Made `New Puzzle` cycle through catalogue entries.
- Added immutable clue cells and editable player-answer cells.
- Styled clues as black/bold and player answers as blue.
- Added `Check Answer`, `Reset Answers`, `New Puzzle`, and `Reveal Solution`.
- Added correct, incorrect, blank, and invalid-cell highlighting.
- Added custom puzzle setup mode.
- Added validation for custom puzzle clues.
- Added keyboard arrow navigation.
- Added Backspace clearing.
- Removed the per-cell clear buttons.
- Added confirmation dialogs before discarding progress.
- Added square cells and visually thicker 3x3 borders.
- Added tests for the solver and catalogue.

## 6. Known limitations

- The solver returns one feasible solution when multiple solutions exist.
- `Check Answer` compares player answers against that returned solution. Therefore, a valid answer belonging to a different solution may currently be marked incorrect.
- Difficulty labels are manually assigned metadata, not calculated by a difficulty-rating algorithm.
- The catalogue currently contains only a small number of puzzles.
- Puzzle generation does not yet exist.
- The application requires IBM CPLEX and its compatible Python package.
- The custom HTML component is browser-facing UI code and has less automated coverage than the Python modules.
- The original `main.ipynb` remains as a historical experiment and may contain hardcoded puzzle data that is not used by the Streamlit app.

## 7. Design decisions to preserve

- Keep the board as a 9x9 grid using integers, with `0` representing blank cells.
- Preserve the public solver entry point:

```python
solve_sudoku(grid)
```

- Preserve `SudokuSolveError` for solver failures.
- Keep puzzle catalogue metadata in `puzzles.json`, rather than hardcoding catalogue entries inside `app.py`.
- Preserve stable puzzle IDs such as `easy-001`.
- Keep naming explicit and descriptive.
- Use type hints and small helper functions.
- Keep immutable clues visually distinct from player answers.
- Do not replace player answers with the solution during `Check Answer`.
- Preserve the separation between solver logic, validation logic, catalogue loading, Streamlit state management, and browser UI.
- New generator functionality should integrate with the existing catalogue and return the same 9x9 grid format.
- Generated puzzles should be validated before being added to the catalogue or loaded into the app.
- The custom component communicates with Python through action dictionaries and should continue following that pattern.
