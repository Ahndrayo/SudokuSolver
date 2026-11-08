from puzzles import available_difficulties, get_puzzle, get_puzzles, get_puzzles_by_difficulty
from validation import validate_grid


def test_catalogue_entries_are_valid_and_have_unique_ids():
    puzzles = get_puzzles()

    assert len(puzzles) == 8
    assert len({puzzle.id for puzzle in puzzles}) == len(puzzles)
    assert all(not validate_grid(puzzle.grid) for puzzle in puzzles)


def test_catalogue_exposes_difficulty_groups():
    assert available_difficulties() == ("Easy", "Medium", "Hard", "Expert")
    assert len(get_puzzles_by_difficulty("Easy")) == 2
    assert len(get_puzzles_by_difficulty("Expert")) == 2


def test_catalogue_lookup_uses_stable_ids():
    puzzle = get_puzzle("easy-001")

    assert puzzle.name == "Classic Starter"
    assert puzzle.difficulty == "Easy"
    assert puzzle.grid[0] == (5, 3, 0, 0, 7, 0, 0, 0, 0)
