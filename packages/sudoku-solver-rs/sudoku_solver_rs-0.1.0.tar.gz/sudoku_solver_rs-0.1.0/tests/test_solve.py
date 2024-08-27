import sudoku_solver_rs


def test_solve():
    sudoku_line = "...2...633....54.1..1..398........9....538....3........263..5..5.37....847...1..."
    assert (
        sudoku_solver_rs.from_str_line(sudoku_line)
        == "854219763397865421261473985785126394649538172132947856926384517513792648478651239"
    )
