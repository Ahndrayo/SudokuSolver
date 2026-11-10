from candidates import candidate_sets, remaining_digit_counts


def test_candidates_exclude_row_column_and_box_values():
    grid = [[0] * 9 for _ in range(9)]
    grid[0][0] = 1
    grid[0][1] = 2
    grid[1][0] = 3
    grid[1][1] = 4

    candidates = candidate_sets(grid)

    assert candidates[0][2] == frozenset({5, 6, 7, 8, 9})


def test_single_missing_digit_is_the_only_candidate():
    grid = [[0] * 9 for _ in range(9)]
    grid[0] = list(range(1, 9)) + [0]

    candidates = candidate_sets(grid)

    assert candidates[0][8] == frozenset({9})


def test_remaining_digit_counts_include_all_populated_cells():
    grid = [[0] * 9 for _ in range(9)]
    grid[0][0] = 1
    grid[0][1] = 1
    grid[1][0] = 5

    remaining = remaining_digit_counts(grid)

    assert remaining[1] == 7
    assert remaining[5] == 8
    assert remaining[2] == 9
