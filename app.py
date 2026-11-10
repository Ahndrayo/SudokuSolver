"""Interactive Streamlit frontend for the Sudoku MILP solver."""

from __future__ import annotations

import streamlit as st

from puzzles import (
    Puzzle,
    available_difficulties,
    get_puzzles,
    get_puzzles_by_difficulty,
)
from solver import SudokuSolveError, solve_sudoku
from sudoku_component import sudoku_grid
from validation import conflicting_cells, validate_grid
from generator import generate_minimal_puzzle


GRID_SIZE = 9
STATE_VERSION = 3


def _empty_grid() -> list[list[int]]:
    return [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]


def _copy_grid(grid: list[list[int]]) -> list[list[int]]:
    return [list(row) for row in grid]


def _catalogue_grid(puzzle: Puzzle) -> list[list[int]]:
    return _copy_grid(puzzle.grid)


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


def _set_puzzle(puzzle: Puzzle) -> None:
    st.session_state.mode = "play"
    st.session_state.clue_grid = _catalogue_grid(puzzle)
    st.session_state.player_grid = _empty_grid()
    st.session_state.setup_grid = _empty_grid()
    st.session_state.solution_grid = None
    st.session_state.check_state = "ready"
    st.session_state.last_result = None
    st.session_state.solve_error = None
    st.session_state.validation_cells = []
    st.session_state.current_puzzle_id = puzzle.id
    st.session_state.current_puzzle_name = puzzle.name
    st.session_state.current_difficulty = puzzle.difficulty
    st.session_state.selected_difficulty = puzzle.difficulty


def _puzzles_for_difficulty(difficulty: str) -> tuple[Puzzle, ...]:
    puzzles = get_puzzles_by_difficulty(difficulty)
    return puzzles or get_puzzles()


def _set_default_puzzle() -> None:
    difficulty = st.session_state.get(
        "selected_difficulty",
        available_difficulties()[0],
    )
    _set_puzzle(_puzzles_for_difficulty(difficulty)[0])


def _set_next_puzzle() -> None:
    puzzles = _puzzles_for_difficulty(st.session_state.selected_difficulty)
    current_id = st.session_state.get("current_puzzle_id")
    current_index = next(
        (index for index, puzzle in enumerate(puzzles) if puzzle.id == current_id),
        -1,
    )
    _set_puzzle(puzzles[(current_index + 1) % len(puzzles)])


def _initialise_state() -> None:
    if st.session_state.get("state_version") != STATE_VERSION:
        st.session_state.state_version = STATE_VERSION
        st.session_state.component_version = 0
        _set_default_puzzle()
        return

    st.session_state.setdefault("component_version", 0)
    st.session_state.setdefault("mode", "play")
    st.session_state.setdefault("clue_grid", _catalogue_grid(get_puzzles()[0]))
    st.session_state.setdefault("player_grid", _empty_grid())
    st.session_state.setdefault("setup_grid", _empty_grid())
    st.session_state.setdefault("solution_grid", None)
    st.session_state.setdefault("check_state", "ready")
    st.session_state.setdefault("last_result", None)
    st.session_state.setdefault("solve_error", None)
    st.session_state.setdefault("validation_cells", [])
    st.session_state.setdefault("selected_difficulty", available_difficulties()[0])
    default_puzzle = get_puzzles()[0]
    st.session_state.setdefault("current_puzzle_id", default_puzzle.id)
    st.session_state.setdefault("current_puzzle_name", default_puzzle.name)
    st.session_state.setdefault("current_difficulty", default_puzzle.difficulty)
    st.session_state.setdefault("generated_puzzle_count", 0)


def _reset_answers() -> None:
    st.session_state.player_grid = _empty_grid()
    st.session_state.solution_grid = None
    st.session_state.check_state = "ready"
    st.session_state.last_result = None
    st.session_state.solve_error = None
    st.session_state.validation_cells = []


def _enter_custom_mode() -> None:
    st.session_state.mode = "setup"
    st.session_state.setup_grid = _empty_grid()
    st.session_state.player_grid = _empty_grid()
    st.session_state.solution_grid = None
    st.session_state.check_state = "ready"
    st.session_state.last_result = None
    st.session_state.solve_error = None
    st.session_state.validation_cells = []


def _keep_custom_grid_with_error(grid: list[list[int]], message: str) -> None:
    st.session_state.setup_grid = _copy_grid(grid)
    st.session_state.validation_cells = conflicting_cells(grid)
    if not st.session_state.validation_cells:
        st.session_state.validation_cells = [
            (row, column)
            for row in range(GRID_SIZE)
            for column in range(GRID_SIZE)
            if grid[row][column]
        ]
    st.session_state.solve_error = message


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
        st.caption("Enter the puzzle clues, then click Create Puzzle.")
        display_grid = st.session_state.setup_grid
        clues = _empty_grid()

    component_result = sudoku_grid(
        grid=display_grid,
        clues=clues,
        solution=st.session_state.solution_grid,
        mode=st.session_state.mode,
        check_state=st.session_state.check_state,
        validation_cells=st.session_state.validation_cells,
        available_difficulties=list(available_difficulties()),
        selected_difficulty=st.session_state.selected_difficulty,
        puzzle_id=(
            st.session_state.current_puzzle_id
            if st.session_state.mode == "play"
            else "custom"
        ),
        puzzle_name=(
            st.session_state.current_puzzle_name
            if st.session_state.mode == "play"
            else "Custom puzzle setup"
        ),
        difficulty=(
            st.session_state.current_difficulty
            if st.session_state.mode == "play"
            else "Custom"
        ),
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
            _set_next_puzzle()
            st.session_state.component_version += 1
            st.rerun()

        elif action == "difficulty" and st.session_state.mode == "play":
            requested_difficulty = component_result.get("difficulty")
            if requested_difficulty in available_difficulties():
                st.session_state.selected_difficulty = requested_difficulty
                _set_default_puzzle()
            st.session_state.component_version += 1
            st.rerun()

        elif action == "generate_puzzle" and st.session_state.mode == "play":
            with st.spinner("Generating a puzzle..."):
                generated = generate_minimal_puzzle()
            st.session_state.generated_puzzle_count += 1
            generated_number = st.session_state.generated_puzzle_count
            _set_puzzle(
                Puzzle(
                    id=f"generated-live-{generated_number:03d}",
                    name=(
                        f"Generated Puzzle ({generated.clue_count} clues)"
                    ),
                    difficulty="Generated",
                    grid=generated.grid,
                )
            )
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

        elif action == "play_mode" and st.session_state.mode == "setup":
            _set_default_puzzle()
            st.session_state.component_version += 1
            st.rerun()

        elif action == "create_puzzle" and st.session_state.mode == "setup":
            errors = validate_grid(visible_grid)
            if errors:
                _keep_custom_grid_with_error(
                    visible_grid,
                    "Invalid puzzle:\n" + "\n".join(errors),
                )
            else:
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
                    st.session_state.validation_cells = []
                except SudokuSolveError as error:
                    _keep_custom_grid_with_error(visible_grid, str(error))

            st.session_state.component_version += 1
            st.rerun()

        elif action == "clear" and st.session_state.mode == "setup":
            st.session_state.setup_grid = _empty_grid()
            st.session_state.solve_error = None
            st.session_state.validation_cells = []
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

