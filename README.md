# Sudoku Solver

This project contains the original notebook experiment plus a reusable
DOcplex MILP solver and a Streamlit frontend.

## Run the web app

From the project directory, activate the existing virtual environment and run:

```powershell
.\.venv\Scripts\Activate.ps1
python -m streamlit run app.py
```

The app starts with a catalogue puzzle whose clues are immutable. Enter answers
in the blue cells, then use `Check Answer`. Correct, incorrect, and blank cells
are highlighted without replacing the player’s entries. The grid also supports
Backspace for clearing and arrow keys for moving between cells.

Use the difficulty selector to choose Easy, Medium, Hard, Expert, or Generated puzzles.
Each puzzle has a stable ID, a name, and a difficulty tag. `New Puzzle` cycles
through the catalogue entries for the selected difficulty.

`Generate Puzzle` creates a new minimal uniquely solvable puzzle for the current
session. It is not automatically added to `puzzles.json`.

Use the `Custom Puzzle` mode to enter your own clues, then click `Create Puzzle`
to validate and lock them before playing. Invalid clues remain on the grid and
are highlighted for correction.

## Generate a minimal puzzle

The backend generator can create a randomized complete solution, remove clues
while preserving uniqueness, and return a minimal uniquely solvable puzzle:

```python
from generator import generate_minimal_puzzle

generated = generate_minimal_puzzle(seed=7)
print(generated.grid)
print(generated.clue_count)
```

Difficulty rating will be added separately; minimal clue count does not by
itself imply a human difficulty level.

While playing, blank cells expose dynamic candidate pencil marks. Candidates
that conflict with an existing value in the same row, column, or box are
disabled and removed from saved notes. The board also shows how many copies of
each digit remain to be placed. Use `Pencil Mode` to switch between permanent
answers and temporary working notes; cells remain empty until a digit is entered
with Pencil Mode off. Invalid pencil attempts identify the conflicting row,
column, or box and briefly highlight the cells involved.

## Run the tests

```powershell
python -m pytest -q
```

The additional frontend and test dependencies are listed in
`requirements-web.txt`. The existing `requirements.txt` is retained as-is.

