"""Puzzle catalogue loading and lookup helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from validation import validate_grid


@dataclass(frozen=True)
class Puzzle:
    """A catalogue entry and its immutable clue grid."""

    id: str
    name: str
    difficulty: str
    grid: tuple[tuple[int, ...], ...]


def _parse_grid(raw_grid: Any, puzzle_id: str) -> tuple[tuple[int, ...], ...]:
    if not isinstance(raw_grid, list) or len(raw_grid) != 9:
        raise ValueError(f"Puzzle {puzzle_id!r} must contain 9 rows.")

    grid: list[tuple[int, ...]] = []
    for row_number, raw_row in enumerate(raw_grid, start=1):
        if not isinstance(raw_row, str) or len(raw_row) != 9:
            raise ValueError(
                f"Puzzle {puzzle_id!r} row {row_number} must be a 9-character string."
            )
        if any(character not in "0123456789" for character in raw_row):
            raise ValueError(
                f"Puzzle {puzzle_id!r} row {row_number} contains a non-digit character."
            )
        grid.append(tuple(int(character) for character in raw_row))

    errors = validate_grid(grid)
    if errors:
        raise ValueError(f"Puzzle {puzzle_id!r} is invalid: {' '.join(errors)}")
    return tuple(grid)


@lru_cache(maxsize=1)
def get_puzzles() -> tuple[Puzzle, ...]:
    """Load and validate every puzzle in the catalogue."""

    catalogue_path = Path(__file__).with_name("puzzles.json")
    with catalogue_path.open(encoding="utf-8") as catalogue_file:
        raw_catalogue = json.load(catalogue_file)

    if not isinstance(raw_catalogue, list):
        raise ValueError("The puzzle catalogue must contain a list of puzzles.")

    puzzles: list[Puzzle] = []
    seen_ids: set[str] = set()
    for raw_puzzle in raw_catalogue:
        if not isinstance(raw_puzzle, dict):
            raise ValueError("Each catalogue entry must be an object.")

        puzzle_id = raw_puzzle.get("id")
        name = raw_puzzle.get("name")
        difficulty = raw_puzzle.get("difficulty")
        if not all(isinstance(value, str) and value for value in (puzzle_id, name, difficulty)):
            raise ValueError("Every puzzle needs non-empty id, name, and difficulty fields.")
        if puzzle_id in seen_ids:
            raise ValueError(f"Duplicate puzzle id: {puzzle_id!r}.")
        seen_ids.add(puzzle_id)

        puzzles.append(
            Puzzle(
                id=puzzle_id,
                name=name,
                difficulty=difficulty,
                grid=_parse_grid(raw_puzzle.get("grid"), puzzle_id),
            )
        )

    if not puzzles:
        raise ValueError("The puzzle catalogue cannot be empty.")
    return tuple(puzzles)


def get_puzzle(puzzle_id: str) -> Puzzle:
    """Return a catalogue entry by stable id."""

    for puzzle in get_puzzles():
        if puzzle.id == puzzle_id:
            return puzzle
    raise KeyError(f"Unknown puzzle id: {puzzle_id!r}.")


def get_puzzles_by_difficulty(difficulty: str) -> tuple[Puzzle, ...]:
    """Return catalogue entries matching a difficulty label."""

    return tuple(
        puzzle for puzzle in get_puzzles() if puzzle.difficulty == difficulty
    )


def available_difficulties() -> tuple[str, ...]:
    """Return difficulty labels in their catalogue order."""

    return tuple(dict.fromkeys(puzzle.difficulty for puzzle in get_puzzles()))
