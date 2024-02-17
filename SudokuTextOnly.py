def is_valid_move(grid: list[list[int]], row: int, col: int, num: int) -> bool:
    for i in range(9):
        # Check if num is in rows
        if grid[row][i] == num:
            return False

        # Check if num is in columns
        if grid[i][col] == num:
            return False

    # Check if num is present in 3x3 block
    corner_row = row - row % 3
    corner_col = col - col % 3
    for x in range(3):
        for y in range(3):
            if grid[corner_row + x][corner_col + y] == num:
                return False

    return True


def solve(grid: list[list[int]], row: int, col: int) -> bool:
    """
    Solves a Sudoku board using backtracking

    :param grid: 2D list of ints
    :param row: the current row 
    :param col: the current column
    :return: boolean if solution is found
    """
    if col > 8:
        # If reached the end of the matrix
        if row == 8:
            return True

        # If reached the end of the column
        row += 1
        col = 0

    # Skip cell if number is already given
    if grid[row][col] > 0:
        return solve(grid, row, col + 1)

    # Check each possible value for the cell
    for num in range(1, 10):
        # Check if valid move
        if is_valid_move(grid, row, col, num):

            grid[row][col] = num

            # Recursively check the next cell in the matrix
            if solve(grid, row, col + 1):
                return True

        # Backtrack cell number back to zero if subsequent moves are invalid
        grid[row][col] = 0

    return False


grid = [[0, 0, 0, 0, 0, 0, 6, 8, 0],
        [0, 0, 0, 0, 7, 3, 0, 0, 9],
        [3, 0, 9, 0, 0, 0, 0, 4, 5],
        [4, 9, 0, 0, 0, 0, 0, 0, 0],
        [8, 0, 3, 0, 5, 0, 9, 0, 2],
        [0, 0, 0, 0, 0, 0, 0, 3, 6],
        [9, 6, 0, 0, 0, 0, 3, 0, 8],
        [7, 0, 0, 6, 8, 0, 0, 0, 0],
        [0, 2, 8, 0, 0, 0, 0, 0, 0]]

if solve(grid, 0, 0):
    for i in range(9):
        for j in range(9):
            print(grid[i][j], end=' ')
            if (j+1) % 3 == 0 and j != 8:
                print('|', end=' ')
        print()
        if (i+1) % 3 == 0 and i != 8:
            for k in range(11):
                print('-', end=' ')
            print()
else:
    print('No solution')
