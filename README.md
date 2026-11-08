# Sudoku Solver

This project contains the original notebook experiment plus a reusable
DOcplex MILP solver and a Streamlit frontend.

## Run the web app

From the project directory, activate the existing virtual environment and run:

```powershell
.\.venv\Scripts\Activate.ps1
python -m streamlit run app.py
```

Enter givens as numbers from 1 to 9 and leave unknown cells blank. The grid
supports Backspace for clearing and arrow keys for moving between cells. The
app validates duplicate givens before building a fresh CPLEX model for each
solve.

## Run the tests

```powershell
python -m pytest -q
```

The additional frontend and test dependencies are listed in
`requirements-web.txt`. The existing `requirements.txt` is retained as-is.

