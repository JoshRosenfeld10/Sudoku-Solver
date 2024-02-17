import pygame
from sys import exit
from random import randint
from Grids import grids
pygame.init()


class Grid:
    def __init__(self, width, height, display):
        self.rows = 9
        self.cols = 9
        self.width = width
        self.height = height
        self.display = display
        self.grid = grids[randint(0, len(grids) - 1)]  # Pick random grid
        self.cubes = [[Cube(self.grid[r][c], r, c, width, height)
                       for c in range(self.cols)] for r in range(self.rows)]
        self.model = None
        self.solved = False
        self.update_model()
        self.problem_cubes = {}

    def update_model(self):
        self.model = [[self.cubes[r][c].value
                       for c in range(self.cols)] for r in range(self.rows)]

    def draw(self):
        # Draw Cubes
        for i in range(self.rows):
            for j in range(self.cols):
                cube = self.cubes[i][j]
                if not self.solved:
                    if cube.value == self.grid[i][j]:
                        # Cannot interact with cubes initially given
                        cube.set_static_value(True)
                    else:
                        cube.set_static_value(False)
                cube.draw(self.display, False, self.problem_cubes)

        # Draw Grid Lines
        gap = self.width / 9
        for i in range(self.rows + 1):
            if i % 3 == 0 and i != 0:
                thickness = 4
            else:
                thickness = 1
            pygame.draw.line(self.display, (0, 0, 0),
                             (0, i * gap), (self.width, i * gap), thickness)
            pygame.draw.line(self.display, (0, 0, 0),
                             (i * gap, 0), (i * gap, self.height), thickness)

    def click_pos(self, pos):
        gap = self.width / 9
        x = int(pos[0] // gap)
        y = int(pos[1] // gap)
        return (x, y)

    def select_cell(self, row_col):
        if row_col[1] > 8 or row_col[0] > 8 or self.solved or self.grid[row_col[1]][row_col[0]] != 0:
            return

        # Deselect all other cells
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].set_selected(False)

        self.cubes[row_col[1]][row_col[0]].set_selected(True)
        self.draw()

    def value_change(self, value):
        # Find selected cell
        for i in range(self.rows):
            for j in range(self.cols):
                if self.cubes[i][j].selected == True:
                    selected_cell = self.cubes[i][j]
                    if selected_cell.value == value:
                        return
                    selected_cell.set_value(value)
                    self.is_valid_move_detection(i, j, selected_cell.value)
                    self.update_model()
                    self.finished()
                    self.draw()

    def is_valid_move_detection(self, row, col, num):
        """
        For drawing the problem cubes
        """
        found = False
        grid = self.model
        curr_cube = grid[row][col]
        problems = []
        for i in range(9):
            # Check if num is in rows or columns
            if grid[row][i] == num and grid[row][i] != curr_cube:
                found = True
                problems.append(self.cubes[row][i])
            if grid[i][col] == num and grid[i][col] != curr_cube:
                found = True
                problems.append(self.cubes[i][col])

        # Check if num is present in 3x3 block
        corner_row = row - row % 3
        corner_col = col - col % 3
        for x in range(3):
            for y in range(3):
                if grid[corner_row + x][corner_col + y] == num and \
                        grid[corner_row + x][corner_col + y] != curr_cube:
                    found = True
                    problems.append(
                        self.cubes[corner_row + x][corner_col + y])

        if found and num != 0:
            # Add the cube itself
            problems.append(self.cubes[row][col])
            self.add_problem_cubes(self.cubes[row][col], problems)
        else:
            self.remove_problem_cubes(self.cubes[row][col])

    def is_valid_move(self, row, col, num):
        """
        For the backtracking algorithm
        """
        grid = self.model
        for i in range(9):
            # Check if num is in rows or columns
            if grid[row][i] == num or grid[i][col] == num:
                return False

        # Check if num is present in 3x3 block
        corner_row = row - row % 3
        corner_col = col - col % 3
        for x in range(3):
            for y in range(3):
                if grid[corner_row + x][corner_col + y] == num:
                    return False

        return True

    def solve(self, row=0, col=0):
        if col > 8:
            # If reached the end of the matrix
            if row == 8:
                return True

            # If reached the end of the column
            row += 1
            col = 0

        curr_cube = self.cubes[row][col]

        # Skip cell if number is already given
        if self.model[row][col] > 0:
            return self.solve(row, col + 1)

        # Check each possible value for the cell
        for num in range(1, 10):
            # Check if valid move
            if self.is_valid_move(row, col, num):

                curr_cube.set_value(num)
                curr_cube.set_correct_value(True)
                curr_cube.draw(self.display, True)
                self.update_model()
                pygame.display.update()
                pygame.time.delay(100)

                # Recursively check the next cell in the matrix
                if self.solve(row, col + 1):
                    return True

            # Backtrack cell number back to zero if subsequent moves are invalid
            curr_cube.set_value(0)
            curr_cube.set_correct_value(False)
            curr_cube.draw(self.display, True)
            self.update_model()
            pygame.display.update()

        return False

    def set_solved(self):
        # Set all cubes to be static
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].set_static_value(True)
                self.cubes[i][j].set_selected(False)

        self.solved = True

    def finished(self):
        if not any(0 in row for row in self.model) and not self.problem_cubes:
            self.set_solved()

    def add_problem_cubes(self, selected_cube, related_cubes: list):
        self.problem_cubes[selected_cube] = related_cubes

    def remove_problem_cubes(self, problem_cube):
        if problem_cube in self.problem_cubes:
            self.problem_cubes.pop(problem_cube)

    def clear_problem_cubes(self):
        self.problem_cubes.clear()


class Cube:
    def __init__(self, value, row, col, width, height):
        self.value = value
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False
        self.correct_value = False
        self.static_value = False

    def draw(self, display, solving=False, problem_cubes=[]):
        font = pygame.font.SysFont(None, 40)

        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        # Check if problem cube
        problem_cube = False
        if problem_cubes:
            for i in problem_cubes:
                if self in problem_cubes[i]:
                    problem_cube = True
                    break

        # White cell background
        pygame.draw.rect(display, (255, 255, 255), (x, y, gap, gap))

        if self.selected:
            if problem_cube:
                pygame.draw.rect(display, (255, 0, 0), (x, y, gap, gap), 3)
            else:
                pygame.draw.rect(display, (148, 148, 148), (x, y, gap, gap), 3)

        if solving or self.value != 0:
            if self.static_value:
                # Black text
                text = font.render(str(self.value), False, (0, 0, 0))
            else:
                # Grey text
                text = font.render(str(self.value), False, (148, 148, 148))

            if problem_cube:
                # Red if problematic
                text = font.render(str(self.value), False, (255, 0, 0))
            display.blit(text, (x + (gap/2 - text.get_width()/2),
                                y + (gap/2 - text.get_height()/2)))

        if solving:
            if self.correct_value:
                # Green box
                pygame.draw.rect(display, (0, 200, 0), (x, y, gap, gap), 3)
            else:
                # Red box
                pygame.draw.rect(display, (255, 0, 0), (x, y, gap, gap), 3)

    def set_selected(self, choice: bool):
        self.selected = choice

    def set_value(self, value):
        self.value = value

    def set_correct_value(self, correct: bool):
        self.correct_value = correct

    def set_static_value(self, value: bool):
        self.static_value = value


def draw_display(display, grid, width, height, counting_time):
    display.fill((255, 255, 255))
    grid.draw()

    # Draw Timer
    font = pygame.font.SysFont(None, 40)
    time = font.render(f'Time: {format_time(counting_time)}', False, (0, 0, 0))
    time_rect = time.get_rect(midright=(
        width-(width/50), width+((height-width)/2)))
    display.blit(time, time_rect)

    if grid.solved:
        draw_solved_message(display, width, height)
    else:
        draw_instructions(display, width, height)


def format_time(counting_time):
    seconds = (counting_time // 1000)
    minutes = seconds // 60
    return f'{minutes}:{"{:02d}".format(seconds % 60)}'


def draw_solved_message(display, width, height):
    font = pygame.font.SysFont(None, 40)

    text = font.render("Solved!", True, (0, 0, 0))
    text_rect = text.get_rect(midleft=(width/60, width + ((height-width)/2)))

    display.blit(text, text_rect)


def draw_instructions(display, width, height):
    text_size = width // 28
    font = pygame.font.SysFont(None, text_size)

    instructions1 = font.render(
        "Select a cell with the mouse to input numbers", True, (0, 0, 0))
    instructions2 = font.render(
        "Press backspace to remove a number from a cell", True, (0, 0, 0))
    instructions3 = font.render(
        "Press space to solve automatically", True, (0, 0, 0))
    instructions2_rect = instructions2.get_rect(
        midleft=(width/60, width + ((height-width)/2)))
    instructions1_rect = instructions1.get_rect(
        bottomleft=instructions2_rect.topleft)
    instructions3_rect = instructions3.get_rect(
        topleft=instructions2_rect.bottomleft)

    display.blit(instructions1, instructions1_rect)
    display.blit(instructions2, instructions2_rect)
    display.blit(instructions3, instructions3_rect)


if __name__ == '__main__':
    pygame.display.set_caption('Sudoku')
    width = 675
    height = 750
    screen = pygame.display.set_mode((width, height))
    grid = Grid(width, width, screen)
    start_time = pygame.time.get_ticks()
    while True:

        if not grid.solved:
            counting_time = pygame.time.get_ticks() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    grid.set_solved()
                    grid.clear_problem_cubes()
                    grid.draw()
                    grid.solve()
                if event.key == pygame.K_1:
                    grid.value_change(1)
                if event.key == pygame.K_2:
                    grid.value_change(2)
                if event.key == pygame.K_3:
                    grid.value_change(3)
                if event.key == pygame.K_4:
                    grid.value_change(4)
                if event.key == pygame.K_5:
                    grid.value_change(5)
                if event.key == pygame.K_6:
                    grid.value_change(6)
                if event.key == pygame.K_7:
                    grid.value_change(7)
                if event.key == pygame.K_8:
                    grid.value_change(8)
                if event.key == pygame.K_9:
                    grid.value_change(9)
                if event.key == pygame.K_BACKSPACE:
                    grid.value_change(0)

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                grid.select_cell(grid.click_pos(pos))

        draw_display(screen, grid, width, height, counting_time)
        pygame.display.update()
