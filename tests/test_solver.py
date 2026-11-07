from solver import SudokuSolveError, solve_sudoku


CHALLENGE = [
    [8, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 3, 6, 0, 0, 0, 0, 0],
    [0, 7, 0, 0, 9, 0, 2, 0, 0],
    [0, 5, 0, 0, 0, 7, 0, 0, 0],
    [0, 0, 0, 0, 4, 5, 7, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 3, 0],
    [0, 0, 1, 0, 0, 0, 0, 6, 8],
    [0, 0, 8, 5, 0, 0, 0, 1, 0],
    [0, 9, 0, 0, 0, 0, 4, 0, 0],
]


def test_solves_challenge_puzzle():
    solution = solve_sudoku(CHALLENGE)

    assert all(sorted(row) == list(range(1, 10)) for row in solution)
    assert all(
        sorted(solution[row][column] for row in range(9)) == list(range(1, 10))
        for column in range(9)
    )
    for row in range(9):
        for column in range(9):
            if CHALLENGE[row][column]:
                assert solution[row][column] == CHALLENGE[row][column]


def test_rejects_duplicate_given():
    invalid = [row[:] for row in CHALLENGE]
    invalid[0][1] = 8

    try:
        solve_sudoku(invalid)
    except SudokuSolveError as error:
        assert "duplicate" in str(error).lower()
    else:
        raise AssertionError("Expected duplicate givens to be rejected")


def test_rejects_out_of_range_value():
    invalid = [row[:] for row in CHALLENGE]
    invalid[0][1] = 10

    try:
        solve_sudoku(invalid)
    except SudokuSolveError as error:
        assert "between 0 and 9" in str(error)
    else:
        raise AssertionError("Expected out-of-range value to be rejected")

