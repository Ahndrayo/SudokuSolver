"""Interactive Streamlit frontend for the Sudoku MILP solver."""

from __future__ import annotations

import streamlit as st

from solver import SudokuSolveError, solve_sudoku


GRID_SIZE = 9


def _empty_grid() -> list[list[int]]:
    return [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]


def _grid_from_session() -> list[list[int]]:
    grid: list[list[int]] = []
    for row in range(GRID_SIZE):
        grid_row: list[int] = []
        for column in range(GRID_SIZE):
            value = st.session_state.get(f"cell_{row}_{column}")
            grid_row.append(0 if value in (None, "") else int(value))
        grid.append(grid_row)
    return grid


def _clear_grid() -> None:
    for row in range(GRID_SIZE):
        for column in range(GRID_SIZE):
            st.session_state[f"cell_{row}_{column}"] = None
    st.session_state.pop("solution", None)
    st.session_state.pop("solve_error", None)


def _load_example() -> None:
    example = _empty_grid()
    example[0] = [5, 3, 0, 0, 7, 0, 0, 0, 0]
    example[1] = [6, 0, 0, 1, 9, 5, 0, 0, 0]
    example[2] = [0, 9, 8, 0, 0, 0, 0, 6, 0]
    for row in range(GRID_SIZE):
        for column in range(GRID_SIZE):
            value = example[row][column]
            st.session_state[f"cell_{row}_{column}"] = value or None
    st.session_state.pop("solution", None)
    st.session_state.pop("solve_error", None)


def _initialise_state() -> None:
    for row in range(GRID_SIZE):
        for column in range(GRID_SIZE):
            st.session_state.setdefault(f"cell_{row}_{column}", None)


def _render_grid_style() -> None:
    st.markdown(
        """
        <style>
        /* Remove gaps between the nine Sudoku columns. */
        [data-testid="stForm"] [data-testid="stHorizontalBlock"]:has(input) {
            gap: 0 !important;
            margin: 0 !important;
        }

        /* Remove vertical spacing between the nine input rows. */
        [data-testid="stForm"] [data-testid="stVerticalBlock"] {
            gap: 0 !important;
        }

        /* Draw a compact border around every cell. */
        [data-testid="stForm"] [data-testid="stHorizontalBlock"]:has(input)
            > [data-testid="stColumn"] {
            min-width: 0 !important;
            padding: 0 !important;
            border-top: 1px solid #333;
            border-left: 1px solid #333;
            border-bottom: 1px solid #333;
        }

        [data-testid="stForm"] [data-testid="stHorizontalBlock"]:has(input)
            > [data-testid="stColumn"]:last-child {
            border-right: 1px solid #333;
        }

        /* Thicker boundaries after columns 3 and 6. */
        [data-testid="stForm"] [data-testid="stHorizontalBlock"]:has(input)
            > [data-testid="stColumn"]:nth-child(3),
        [data-testid="stForm"] [data-testid="stHorizontalBlock"]:has(input)
            > [data-testid="stColumn"]:nth-child(6) {
            border-right: 3px solid #111;
        }

        [data-testid="stForm"] [data-testid="stHorizontalBlock"]:has(input)
            input {
            height: 4.5rem;
            min-height: 4.5rem;
            padding: 0 !important;
            text-align: center;
            font-size: 1.35rem;
            border: 0 !important;
            border-radius: 0 !important;
            background-color: #fff !important;
        }

        [data-testid="stForm"] [data-testid="stHorizontalBlock"]:has(input)
            [data-testid="stNumberInputContainer"] {
            height: 4.5rem;
            min-height: 4.5rem;
            background-color: #fff !important;
        }

        [data-testid="stForm"] [data-testid="stHorizontalBlock"]:has(input)
            [data-baseweb="input"] {
            height: 4.5rem;
            background-color: #fff !important;
        }

        [data-testid="stForm"] [data-testid="stMarkdownContainer"]:has(.sudoku-row-divider) {
            height: 3px !important;
            min-height: 3px !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        .sudoku-row-divider {
            width: 100%;
            height: 3px;
            margin: 0 !important;
            padding: 0 !important;
            background-color: #111;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="Sudoku Solver", page_icon="🔢")
    _initialise_state()

    st.title("Sudoku Solver")
    st.caption("Enter givens as numbers from 1 to 9. Leave unknown cells blank.")
    _render_grid_style()

    with st.form("sudoku_form"):
        for row in range(GRID_SIZE):
            columns = st.columns(GRID_SIZE)
            for column, container in enumerate(columns):
                with container:
                    st.number_input(
                        f"R{row + 1}C{column + 1}",
                        min_value=1,
                        max_value=9,
                        step=1,
                        format="%d",
                        value=None,
                        placeholder="",
                        key=f"cell_{row}_{column}",
                        label_visibility="collapsed",
                    )

            if row in (2, 5):
                st.markdown(
                    '<div class="sudoku-row-divider"></div>',
                    unsafe_allow_html=True,
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

