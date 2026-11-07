"""Validation helpers for Sudoku grids."""

from __future__ import annotations

from collections.abc import Sequence


GRID_SIZE = 9
BOX_SIZE = 3


def validate_grid(grid: Sequence[Sequence[int]]) -> list[str]:
    """Return human-readable validation errors for a Sudoku grid.

    Empty cells are represented by 0. Validation checks the givens only, so
    an incomplete but otherwise consistent puzzle is accepted.
    """

    errors: list[str] = []

    try:
        row_count = len(grid)
    except TypeError:
        return ["The grid must contain 9 rows."]

    if row_count != GRID_SIZE:
        return ["The grid must contain exactly 9 rows."]

    valid_shape = True
    for row_index, row in enumerate(grid):
        try:
            column_count = len(row)
        except TypeError:
            errors.append(f"Row {row_index + 1} is not a valid row.")
            valid_shape = False
            continue

        if column_count != GRID_SIZE:
            errors.append(
                f"Row {row_index + 1} must contain exactly 9 cells."
            )
            valid_shape = False
            continue

        for column_index, value in enumerate(row):
            if isinstance(value, bool) or not isinstance(value, int):
                errors.append(
                    f"Cell ({row_index + 1}, {column_index + 1}) must be an integer from 0 to 9."
                )
            elif not 0 <= value <= 9:
                errors.append(
                    f"Cell ({row_index + 1}, {column_index + 1}) must be between 0 and 9."
                )

    if not valid_shape:
        return errors

    errors.extend(_duplicate_errors(grid))
    return errors


def _duplicate_errors(grid: Sequence[Sequence[int]]) -> list[str]:
    errors: list[str] = []

    for row_index, row in enumerate(grid):
        duplicates = _duplicates(row)
        if duplicates:
            values = ", ".join(str(value) for value in duplicates)
            errors.append(f"Row {row_index + 1} contains duplicate value(s): {values}.")

    for column_index in range(GRID_SIZE):
        duplicates = _duplicates(
            grid[row_index][column_index] for row_index in range(GRID_SIZE)
        )
        if duplicates:
            values = ", ".join(str(value) for value in duplicates)
            errors.append(
                f"Column {column_index + 1} contains duplicate value(s): {values}."
            )

    for box_row in range(0, GRID_SIZE, BOX_SIZE):
        for box_column in range(0, GRID_SIZE, BOX_SIZE):
            values = (
                grid[row_index][column_index]
                for row_index in range(box_row, box_row + BOX_SIZE)
                for column_index in range(box_column, box_column + BOX_SIZE)
            )
            duplicates = _duplicates(values)
            if duplicates:
                box_number = (box_row // BOX_SIZE) * BOX_SIZE + box_column // BOX_SIZE + 1
                duplicate_values = ", ".join(str(value) for value in duplicates)
                errors.append(
                    f"3x3 box {box_number} contains duplicate value(s): {duplicate_values}."
                )

    return errors


def _duplicates(values: Sequence[int] | object) -> list[int]:
    seen: set[int] = set()
    duplicates: set[int] = set()
    for value in values:  # type: ignore[union-attr]
        if value == 0:
            continue
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)

