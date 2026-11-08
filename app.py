"""Interactive Streamlit frontend for the Sudoku MILP solver."""

from __future__ import annotations

import streamlit as st

from solver import SudokuSolveError, solve_sudoku
from sudoku_component import sudoku_grid


GRID_SIZE = 9


def _empty_grid() -> list[list[int]]:
    return [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]


def _example_grid() -> list[list[int]]:
    return [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [0, 0, 0, 0, 6, 0, 0, 0, 3],
        [0, 0, 8, 0, 0, 3, 0, 0, 1],
        [0, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]


def _initialise_state() -> None:
    st.session_state.setdefault("input_grid", _empty_grid())
    st.session_state.setdefault("component_version", 0)


def _clear_grid() -> None:
    st.session_state.input_grid = _empty_grid()
    st.session_state.pop("solution", None)
    st.session_state.pop("solve_error", None)


def _load_example() -> None:
    st.session_state.input_grid = _example_grid()
    st.session_state.pop("solution", None)
    st.session_state.pop("solve_error", None)


def main() -> None:
    st.set_page_config(page_title="Sudoku Solver", page_icon="🔢")
    _initialise_state()

    st.title("Sudoku Solver")
    st.caption("Enter givens as numbers from 1 to 9. Leave unknown cells blank.")

    component_result = sudoku_grid(
        grid=st.session_state.input_grid,
        key=f"sudoku_grid_{st.session_state.component_version}",
    )

    if component_result:
        action = component_result.get("action")
        grid = component_result.get("grid", st.session_state.input_grid)

        if action == "solve":
            st.session_state.input_grid = grid
            try:
                st.session_state.solution = solve_sudoku(grid)
                st.session_state.pop("solve_error", None)
            except SudokuSolveError as error:
                st.session_state.solution = None
                st.session_state.solve_error = str(error)

            st.session_state.component_version += 1
            st.rerun()

        elif action == "clear":
            _clear_grid()
            st.session_state.component_version += 1
            st.rerun()

        elif action == "load_example":
            _load_example()
            st.session_state.component_version += 1
            st.rerun()

    if st.session_state.get("solve_error"):
        st.error(st.session_state.solve_error)

    solution = st.session_state.get("solution")
    if solution:
        st.subheader("Solution")
        for row in solution:
            st.code(" ".join(str(value) for value in row), language=None)


if __name__ == "__main__":
    main()

