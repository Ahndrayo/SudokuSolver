"""Interactive Streamlit frontend for the Sudoku MILP solver."""

from __future__ import annotations

import streamlit as st

from solver import SudokuSolveError, solve_sudoku
from sudoku_component import sudoku_grid


GRID_SIZE = 9
STATE_VERSION = 2


def _empty_grid() -> list[list[int]]:
    return [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]


def _example_grid() -> list[list[int]]:
    return [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]


def _copy_grid(grid: list[list[int]]) -> list[list[int]]:
    return [row[:] for row in grid]


def _player_grid_from_visible(
    visible_grid: list[list[int]],
    clue_grid: list[list[int]],
) -> list[list[int]]:
    return [
        [
            0 if clue_grid[row][column] else visible_grid[row][column]
            for column in range(GRID_SIZE)
        ]
        for row in range(GRID_SIZE)
    ]


def _set_default_puzzle() -> None:
    st.session_state.mode = "play"
    st.session_state.clue_grid = _example_grid()
    st.session_state.player_grid = _empty_grid()
    st.session_state.setup_grid = _empty_grid()
    st.session_state.solution_grid = None
    st.session_state.check_state = "ready"
    st.session_state.last_result = None
    st.session_state.solve_error = None


def _initialise_state() -> None:
    if st.session_state.get("state_version") != STATE_VERSION:
        st.session_state.state_version = STATE_VERSION
        st.session_state.component_version = 0
        _set_default_puzzle()
        return

    st.session_state.setdefault("component_version", 0)
    st.session_state.setdefault("mode", "play")
    st.session_state.setdefault("clue_grid", _example_grid())
    st.session_state.setdefault("player_grid", _empty_grid())
    st.session_state.setdefault("setup_grid", _empty_grid())
    st.session_state.setdefault("solution_grid", None)
    st.session_state.setdefault("check_state", "ready")
    st.session_state.setdefault("last_result", None)
    st.session_state.setdefault("solve_error", None)


def _reset_answers() -> None:
    st.session_state.player_grid = _empty_grid()
    st.session_state.solution_grid = None
    st.session_state.check_state = "ready"
    st.session_state.last_result = None
    st.session_state.solve_error = None


def _enter_custom_mode() -> None:
    st.session_state.mode = "setup"
    st.session_state.setup_grid = _empty_grid()
    st.session_state.solve_error = None


def _evaluate_answers(
    player_grid: list[list[int]],
    clue_grid: list[list[int]],
    solution_grid: list[list[int]],
) -> dict[str, int | bool]:
    correct = 0
    incorrect = 0
    blank = 0
    total_answer_cells = 0

    for row in range(GRID_SIZE):
        for column in range(GRID_SIZE):
            if clue_grid[row][column]:
                continue

            total_answer_cells += 1
            value = player_grid[row][column]
            if value == 0:
                blank += 1
            elif value == solution_grid[row][column]:
                correct += 1
            else:
                incorrect += 1

    return {
        "correct": correct,
        "incorrect": incorrect,
        "blank": blank,
        "complete": total_answer_cells == correct,
    }


def _solve_clues(clue_grid: list[list[int]]) -> list[list[int]]:
    return solve_sudoku(clue_grid)


def main() -> None:
    st.set_page_config(page_title="Sudoku Solver", page_icon="🔢")
    _initialise_state()

    st.title("Sudoku Solver")
    if st.session_state.mode == "play":
        st.caption("Black numbers are clues. Enter your answers in the blue cells.")
        display_grid = st.session_state.player_grid
        clues = st.session_state.clue_grid
    else:
        st.caption("Enter the puzzle clues, then click Start Puzzle.")
        display_grid = st.session_state.setup_grid
        clues = _empty_grid()

    component_result = sudoku_grid(
        grid=display_grid,
        clues=clues,
        solution=st.session_state.solution_grid,
        mode=st.session_state.mode,
        check_state=st.session_state.check_state,
        key=f"sudoku_grid_{st.session_state.component_version}",
    )

    if component_result:
        action = component_result.get("action")
        visible_grid = component_result.get("grid", display_grid)

        if action == "check" and st.session_state.mode == "play":
            player_grid = _player_grid_from_visible(
                visible_grid,
                st.session_state.clue_grid,
            )
            try:
                solution_grid = st.session_state.solution_grid or _solve_clues(
                    st.session_state.clue_grid
                )
                st.session_state.player_grid = player_grid
                st.session_state.solution_grid = solution_grid
                result = _evaluate_answers(
                    player_grid,
                    st.session_state.clue_grid,
                    solution_grid,
                )
                st.session_state.last_result = result
                st.session_state.check_state = (
                    "complete" if result["complete"] else "checked"
                )
                st.session_state.solve_error = None
            except SudokuSolveError as error:
                st.session_state.solve_error = str(error)

            st.session_state.component_version += 1
            st.rerun()

        elif action == "reset_answers" and st.session_state.mode == "play":
            _reset_answers()
            st.session_state.component_version += 1
            st.rerun()

        elif action == "new_puzzle":
            _set_default_puzzle()
            st.session_state.component_version += 1
            st.rerun()

        elif action == "reveal" and st.session_state.mode == "play":
            try:
                solution_grid = st.session_state.solution_grid or _solve_clues(
                    st.session_state.clue_grid
                )
                st.session_state.solution_grid = solution_grid
                st.session_state.player_grid = _copy_grid(solution_grid)
                st.session_state.check_state = "revealed"
                st.session_state.last_result = None
                st.session_state.solve_error = None
            except SudokuSolveError as error:
                st.session_state.solve_error = str(error)

            st.session_state.component_version += 1
            st.rerun()

        elif action == "custom_puzzle" and st.session_state.mode == "play":
            _enter_custom_mode()
            st.session_state.component_version += 1
            st.rerun()

        elif action == "start_puzzle" and st.session_state.mode == "setup":
            try:
                solution_grid = _solve_clues(visible_grid)
                st.session_state.mode = "play"
                st.session_state.clue_grid = _copy_grid(visible_grid)
                st.session_state.player_grid = _empty_grid()
                st.session_state.setup_grid = _empty_grid()
                st.session_state.solution_grid = solution_grid
                st.session_state.check_state = "ready"
                st.session_state.last_result = None
                st.session_state.solve_error = None
            except SudokuSolveError as error:
                st.session_state.solve_error = str(error)

            st.session_state.component_version += 1
            st.rerun()

        elif action == "clear_board" and st.session_state.mode == "setup":
            st.session_state.setup_grid = _empty_grid()
            st.session_state.solve_error = None
            st.session_state.component_version += 1
            st.rerun()

        elif action == "cancel_custom" and st.session_state.mode == "setup":
            _set_default_puzzle()
            st.session_state.component_version += 1
            st.rerun()

    if st.session_state.solve_error:
        st.error(st.session_state.solve_error)

    result = st.session_state.last_result
    if result and st.session_state.check_state == "complete":
        st.success("Puzzle complete!")
    elif result:
        st.info(
            f"Correct: {result['correct']} · "
            f"Incorrect: {result['incorrect']} · "
            f"Blank: {result['blank']}"
        )


if __name__ == "__main__":
    main()

