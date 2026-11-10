from generator import (
    generate_minimal_puzzle,
    generate_solution,
    has_unique_solution,
)
from validation import validate_grid


def _is_complete_solution(grid):
    return (
        not validate_grid(grid)
        and all(value != 0 for row in grid for value in row)
        and all(sorted(row) == list(range(1, 10)) for row in grid)
        and all(
            sorted(grid[row][column] for row in range(9)) == list(range(1, 10))
            for column in range(9)
        )
    )


def test_generate_solution_returns_a_complete_valid_grid():
    solution = generate_solution(seed=7)

    assert _is_complete_solution(solution)


def test_empty_grid_has_an_alternative_solution():
    assert not has_unique_solution([[0] * 9 for _ in range(9)])


def test_generated_puzzle_is_unique_and_minimal():
    generated = generate_minimal_puzzle(seed=7)

    assert 0 < generated.clue_count < 81
    assert has_unique_solution(generated.grid, generated.solution)

    for row in range(9):
        for column in range(9):
            if not generated.grid[row][column]:
                continue

            candidate = [list(candidate_row) for candidate_row in generated.grid]
            candidate[row][column] = 0
            assert not has_unique_solution(candidate, generated.solution)
