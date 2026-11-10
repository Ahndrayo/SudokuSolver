"""DOcplex MILP solver for 9x9 Sudoku puzzles."""

from __future__ import annotations

from collections.abc import Sequence

from docplex.mp.model import Model

from validation import validate_grid


GRID_SIZE = 9
VALUES = range(1, GRID_SIZE + 1)


class SudokuSolveError(ValueError):
    """Raised when a Sudoku grid is invalid or has no feasible solution."""


def solve_sudoku(grid: Sequence[Sequence[int]]) -> list[list[int]]:
    """Solve a Sudoku grid and return a new 9x9 solution.

    Empty cells must be represented by 0. A fresh model is built on each
    call, keeping repeated UI solves independent from one another.
    """

    errors = validate_grid(grid)
    if errors:
        raise SudokuSolveError("Invalid puzzle:\n" + "\n".join(errors))

    model, x, _ = _build_model()

    for row in range(GRID_SIZE):
        for column in range(GRID_SIZE):
            value = grid[row][column]
            if value:
                model.add_constraint(x[row, column] == value)

    solution = model.solve(log_output=False)
    if solution is None:
        raise SudokuSolveError("This puzzle has no feasible solution.")

    return [
        [int(round(x[row, column].solution_value)) for column in range(GRID_SIZE)]
        for row in range(GRID_SIZE)
    ]


def _build_model() -> tuple[
    Model,
    dict[tuple[int, int], object],
    dict[tuple[int, int, int], object],
]:
    """Create the base Sudoku model without puzzle-specific givens."""

    model = Model(name="Sudoku Model")
    x = {
        (row, column): model.integer_var(
            lb=1,
            ub=GRID_SIZE,
            name=f"Row {row + 1}, Column {column + 1}",
        )
        for row in range(GRID_SIZE)
        for column in range(GRID_SIZE)
    }
    p = {
        (row, column, value): model.binary_var(
            name=f"Value {value} present in Row {row + 1}, Column {column + 1}"
        )
        for row in range(GRID_SIZE)
        for column in range(GRID_SIZE)
        for value in VALUES
    }

    for row in range(GRID_SIZE):
        for value in VALUES:
            model.add_constraint(
                model.sum(p[row, column, value] for column in range(GRID_SIZE)) == 1
            )

    for column in range(GRID_SIZE):
        for value in VALUES:
            model.add_constraint(
                model.sum(p[row, column, value] for row in range(GRID_SIZE)) == 1
            )

    for box_row in range(0, GRID_SIZE, 3):
        for box_column in range(0, GRID_SIZE, 3):
            for value in VALUES:
                model.add_constraint(
                    model.sum(
                        p[row, column, value]
                        for row in range(box_row, box_row + 3)
                        for column in range(box_column, box_column + 3)
                    )
                    == 1
                )

    for row in range(GRID_SIZE):
        for column in range(GRID_SIZE):
            model.add_constraint(
                x[row, column]
                == model.sum(value * p[row, column, value] for value in VALUES)
            )
            model.add_constraint(
                model.sum(p[row, column, value] for value in VALUES) == 1
            )

    return model, x, p

