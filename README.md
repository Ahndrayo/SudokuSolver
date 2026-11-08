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

Use the difficulty selector to choose Easy, Medium, Hard, or Expert puzzles.
Each puzzle has a stable ID, a name, and a difficulty tag. `New Puzzle` cycles
through the catalogue entries for the selected difficulty.

Use the `Custom Puzzle` mode to enter your own clues, then click `Create Puzzle`
to validate and lock them before playing. Invalid clues remain on the grid and
are highlighted for correction.

## Run the tests

```powershell
python -m pytest -q
```

The additional frontend and test dependencies are listed in
`requirements-web.txt`. The existing `requirements.txt` is retained as-is.

