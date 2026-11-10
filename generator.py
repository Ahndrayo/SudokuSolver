"""Generate uniquely solvable Sudoku puzzles with DOcplex and CPLEX."""

from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass

from solver import GRID_SIZE, VALUES, SudokuSolveError, _build_model, solve_sudoku
from validation import validate_grid


Grid = Sequence[Sequence[int]]


@dataclass(frozen=True)
class GeneratedPuzzle:
    """A generated clue grid together with its known complete solution."""

    grid: tuple[tuple[int, ...], ...]
    solution: tuple[tuple[int, ...], ...]
    clue_count: int
    seed: int | None


def generate_solution(seed: int | None = None) -> list[list[int]]:
    """Generate a complete valid Sudoku grid using a random objective."""

    rng = random.Random(seed)
    model, x, p = _build_model()
    model.minimize(
        model.sum(
            rng.randint(-1_000_000, 1_000_000) * p[row, column, value]
            for row in range(GRID_SIZE)
            for column in range(GRID_SIZE)
            for value in VALUES
        )
    )

    if model.solve(log_output=False) is None:
        raise SudokuSolveError("Could not generate a complete Sudoku solution.")

    return [
        [int(round(x[row, column].solution_value)) for column in range(GRID_SIZE)]
        for row in range(GRID_SIZE)
    ]


def find_alternative_solution(
    grid: Grid,
    known_solution: Grid | None = None,
) -> list[list[int]] | None:
    """Return a solution different from ``known_solution``, if one exists.

    The known solution must be a complete solution compatible with ``grid``.
    If it is omitted, one solution is found first and then excluded.
    """

    errors = validate_grid(grid)
    if errors:
        raise SudokuSolveError("Invalid puzzle:\n" + "\n".join(errors))

    if known_solution is None:
        known_solution = solve_sudoku(grid)

    solution_errors = validate_grid(known_solution)
    if solution_errors or any(
        known_solution[row][column] == 0
        for row in range(GRID_SIZE)
        for column in range(GRID_SIZE)
    ):
        raise SudokuSolveError("The known solution must be a complete valid grid.")

    for row in range(GRID_SIZE):
        for column in range(GRID_SIZE):
            clue = grid[row][column]
            if clue and clue != known_solution[row][column]:
                raise SudokuSolveError(
                    "The known solution is incompatible with the puzzle clues."
                )

    model, x, p = _build_model()
    for row in range(GRID_SIZE):
        for column in range(GRID_SIZE):
            clue = grid[row][column]
            if clue:
                model.add_constraint(x[row, column] == clue)

    model.add_constraint(
        model.sum(
            p[row, column, known_solution[row][column]]
            for row in range(GRID_SIZE)
            for column in range(GRID_SIZE)
        )
        <= GRID_SIZE * GRID_SIZE - 1
    )

    if model.solve(log_output=False) is None:
        return None

    return [
        [int(round(x[row, column].solution_value)) for column in range(GRID_SIZE)]
        for row in range(GRID_SIZE)
    ]


def has_unique_solution(grid: Grid, known_solution: Grid | None = None) -> bool:
    """Return whether a puzzle has exactly one solution."""

    return find_alternative_solution(grid, known_solution) is None


def generate_minimal_puzzle(seed: int | None = None) -> GeneratedPuzzle:
    """Generate a uniquely solvable puzzle with no safely removable clues."""

    solution = generate_solution(seed)
    clue_grid = [row[:] for row in solution]
    rng = random.Random(seed)
    positions = [
        (row, column)
        for row in range(GRID_SIZE)
        for column in range(GRID_SIZE)
    ]
    rng.shuffle(positions)

    for row, column in positions:
        removed_clue = clue_grid[row][column]
        clue_grid[row][column] = 0

        if find_alternative_solution(clue_grid, solution) is not None:
            clue_grid[row][column] = removed_clue

    return GeneratedPuzzle(
        grid=tuple(tuple(row) for row in clue_grid),
        solution=tuple(tuple(row) for row in solution),
        clue_count=sum(value != 0 for row in clue_grid for value in row),
        seed=seed,
    )
