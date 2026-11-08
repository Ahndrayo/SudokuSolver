"""Local Streamlit component for the interactive Sudoku grid."""

from __future__ import annotations

from pathlib import Path

import streamlit.components.v1 as components


_COMPONENT = components.declare_component(
    "sudoku_grid",
    path=str(Path(__file__).parent / "sudoku_component"),
)


def sudoku_grid(*, grid: list[list[int]], key: str) -> dict | None:
    """Render the Sudoku grid and return an action when a button is pressed."""

    return _COMPONENT(grid=grid, key=key, default=None)

