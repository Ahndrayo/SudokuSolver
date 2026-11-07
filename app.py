"""Interactive Streamlit frontend for the Sudoku MILP solver."""

from __future__ import annotations

import streamlit as st

from solver import SudokuSolveError, solve_sudoku


GRID_SIZE = 9


def _empty_grid() -> list[list[int]]:
    return [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]


def _grid_from_session() -> list[list[int]]:
    return [
        [
            int(st.session_state.get(f"cell_{row}_{column}", 0))
            for column in range(GRID_SIZE)
        ]
        for row in range(GRID_SIZE)
    ]


def _clear_grid() -> None:
    for row in range(GRID_SIZE):
        for column in range(GRID_SIZE):
            st.session_state[f"cell_{row}_{column}"] = 0
    st.session_state.pop("solution", None)
    st.session_state.pop("solve_error", None)


def _load_example() -> None:
    example = _empty_grid()
    example[0] = [5, 3, 0, 0, 7, 0, 0, 0, 0]
    example[1] = [6, 0, 0, 1, 9, 5, 0, 0, 0]
    example[2] = [0, 9, 8, 0, 0, 0, 0, 6, 0]
    for row in range(GRID_SIZE):
        for column in range(GRID_SIZE):
            st.session_state[f"cell_{row}_{column}"] = example[row][column]
    st.session_state.pop("solution", None)
    st.session_state.pop("solve_error", None)


def _initialise_state() -> None:
    for row in range(GRID_SIZE):
        for column in range(GRID_SIZE):
            st.session_state.setdefault(f"cell_{row}_{column}", 0)


def main() -> None:
    st.set_page_config(page_title="Sudoku Solver", page_icon="🔢")
    _initialise_state()

    st.title("Sudoku Solver")
    st.caption("Enter givens as numbers from 1 to 9. Leave unknown cells as 0.")

    with st.form("sudoku_form"):
        for row in range(GRID_SIZE):
            columns = st.columns(GRID_SIZE)
            for column, container in enumerate(columns):
                with container:
                    st.number_input(
                        f"R{row + 1}C{column + 1}",
                        min_value=0,
                        max_value=9,
                        step=1,
                        format="%d",
                        key=f"cell_{row}_{column}",
                        label_visibility="collapsed",
                    )

        solve_column, clear_column, example_column = st.columns(3)
        with solve_column:
            submitted = st.form_submit_button("Solve", type="primary")
        with clear_column:
            clear = st.form_submit_button("Clear")
        with example_column:
            load_example = st.form_submit_button("Load example")

    if submitted:
        try:
            st.session_state.solution = solve_sudoku(_grid_from_session())
            st.session_state.pop("solve_error", None)
        except SudokuSolveError as error:
            st.session_state.solution = None
            st.session_state.solve_error = str(error)

    if clear:
        _clear_grid()
        st.rerun()

    if load_example:
        _load_example()
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

