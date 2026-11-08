"""Local Streamlit component for the interactive Sudoku grid."""

from __future__ import annotations

from pathlib import Path

import streamlit.components.v1 as components


_COMPONENT = components.declare_component(
    "sudoku_grid",
    path=str(Path(__file__).parent / "sudoku_component"),
)


def sudoku_grid(
    *,
    grid: list[list[int]],
    clues: list[list[int]],
    solution: list[list[int]] | None,
    mode: str,
    check_state: str,
    validation_cells: list[tuple[int, int]],
    available_difficulties: list[str],
    selected_difficulty: str,
    puzzle_id: str,
    puzzle_name: str,
    difficulty: str,
    key: str,
) -> dict | None:
    """Render the Sudoku grid and return an action when a button is pressed."""

    return _COMPONENT(
        grid=grid,
        clues=clues,
        solution=solution,
        mode=mode,
        check_state=check_state,
        validation_cells=validation_cells,
        available_difficulties=available_difficulties,
        selected_difficulty=selected_difficulty,
        puzzle_id=puzzle_id,
        puzzle_name=puzzle_name,
        difficulty=difficulty,
        key=key,
        default=None,
    )

