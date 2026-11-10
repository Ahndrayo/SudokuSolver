"""Candidate and digit-count calculations for Sudoku grids."""

from __future__ import annotations

from collections.abc import Sequence


GRID_SIZE = 9
BOX_SIZE = 3
DIGITS = frozenset(range(1, GRID_SIZE + 1))


def candidate_sets(
    grid: Sequence[Sequence[int]],
) -> tuple[tuple[frozenset[int], ...], ...]:
    """Return legal candidates for every blank cell in ``grid``.

    Filled cells receive an empty candidate set. Candidates are based only on
    the standard row, column, and 3x3-box restrictions.
    """

    _validate_shape(grid)
    candidates: list[list[frozenset[int]]] = []

    for row in range(GRID_SIZE):
        candidate_row: list[frozenset[int]] = []
        for column in range(GRID_SIZE):
            if grid[row][column]:
                candidate_row.append(frozenset())
                continue

            used = set(grid[row])
            used.update(grid[other_row][column] for other_row in range(GRID_SIZE))
            used.update(
                grid[box_row][box_column]
                for box_row in range(row // BOX_SIZE * BOX_SIZE, row // BOX_SIZE * BOX_SIZE + BOX_SIZE)
                for box_column in range(
                    column // BOX_SIZE * BOX_SIZE,
                    column // BOX_SIZE * BOX_SIZE + BOX_SIZE,
                )
            )
            used.discard(0)
            candidate_row.append(frozenset(DIGITS - used))
        candidates.append(candidate_row)

    return tuple(tuple(row) for row in candidates)


def remaining_digit_counts(grid: Sequence[Sequence[int]]) -> dict[int, int]:
    """Return how many occurrences of each digit remain to be placed."""

    _validate_shape(grid)
    counts = {digit: 0 for digit in DIGITS}
    for row in grid:
        for value in row:
            if value in counts:
                counts[value] += 1

    return {digit: GRID_SIZE - counts[digit] for digit in sorted(DIGITS)}


def _validate_shape(grid: Sequence[Sequence[int]]) -> None:
    if len(grid) != GRID_SIZE or any(len(row) != GRID_SIZE for row in grid):
        raise ValueError("The grid must contain exactly 9 rows of 9 cells.")
