import random
import gymnasium


def create_battleship_board(width, height):
    """
    Creates a 2D array representing a Battleship game board,
    initialized with water ('.') in all cells.

    Parameters:
    - width (int): The width of the board.
    - height (int): The height of the board.

    Returns:
    - list of lists: 2D array representing the game board.
    """
    # Initialize the board with water ('.') in all cells
    board = [['.' for _ in range(width)] for _ in range(height)]
    return board


def can_place_ship(board, row, col, size, is_vertical):
    """Check if a ship can be placed on the board."""
    if is_vertical:
        if row + size > len(board):
            return False
        for i in range(size):
            if board[row + i][col] != '.':
                return False
    else:  # Horizontal
        if col + size > len(board[0]):
            return False
        for i in range(size):
            if board[row][col + i] != '.':
                return False
    return True


def place_ship(board, row, col, size, is_vertical, ship_symbol):
    """Place a ship on the board."""
    if is_vertical:
        for i in range(size):
            board[row + i][col] = ship_symbol
    else:  # Horizontal
        for i in range(size):
            board[row][col + i] = ship_symbol


def create_and_fill_battleship_board(width, height, ships, num_each_type=2):
    """Create a Battleship board and fill it with ships, placing 2 of each type."""
    board = [['.' for _ in range(width)] for _ in range(height)]
    for ship_symbol, size in ships.items():
        # for num in range(1, 3):  # Place two of each ship
        for num in range(1, num_each_type + 1):  # Place two of each ship
            placed = False
            while not placed:
                row = random.randint(0, height - 1)
                col = random.randint(0, width - 1)
                is_vertical = random.choice([True, False])
                if can_place_ship(board, row, col, size, is_vertical):
                    # Append a number to the ship symbol to distinguish the ships
                    place_ship(board, row, col, size, is_vertical, ship_symbol)  # + str(num)
                    placed = True
    return board


def check_hit(board, row, col):
    """
    Checks if a shot hits a ship on the board.

    Parameters:
    - board (list of lists): The game board.
    - row (int): The row of the shot.
    - col (int): The column of the shot.

    Returns:
    - bool: True if a ship is hit, False otherwise.
    """
    # Check if the coordinates are within the board boundaries
    if 0 <= row < len(board) and 0 <= col < len(board[0]):
        # Check if there is a ship at the specified location
        if board[row][col] not in ['.', 'O', 'X']:  # '.' for water, 'O' for miss, 'X' for hit
            # Mark the hit on the board
            board[row][col] = 'X'
            return True
        else:
            # Mark the miss on the board if it's not already marked as a hit
            # if board[row][col] != 'X':
            if board[row][col] == '.':
                board[row][col] = 'O'
    return False


# Ships to be placed on the board
ships = {
    'C': 5,  # Carrier
    'B': 4,  # Battleship
    'R': 3,  # Cruiser
    'S': 3,  # Submarine
    'D': 2  # Destroyer
}


class BattleshipBoard(object):
    def __init__(self, width, height, num_each_type=2, exclude_ships=[]):
        self.width = width
        self.height = height
        self.ships = {s: ships[s] for s in ships if s not in exclude_ships}
        self.board = create_and_fill_battleship_board(width, height, self.ships, num_each_type=num_each_type)
        self.shots = [['.' for _ in range(width)] for _ in range(height)]
        self.hits = 0
        self.misses = 0

    def check_shot(self, row, col):
        is_hit = check_hit(self.board, row, col)
        if is_hit:
            self.hits += 1
            self.shots[row][col] = 'X'
        else:
            self.misses += 1
            if self.shots[row][col] == '.':
                self.shots[row][col] = 'O'
        return is_hit

    def check_terminate(self):
        return self.hits == sum(self.ships.values())

    def get_board(self):
        return self.board

    def get_shots(self):
        return self.shots

    def get_shots_overlay_board(self):
        # this is the self-view of the board, where the player can see their own board
        # we can make a choice on whether to show O or show . instead
        shots_overlay_board = [[self.board[row][col] if self.shots[row][col] == '.' else self.shots[row][col] for col in range(self.width)] for row in range(self.height)]
        return shots_overlay_board

    def get_hits(self):
        return self.hits

    def get_misses(self):
        return self.misses

    def get_game_status(self):
        if self.hits == sum(self.ships.values()):
            return 'Game Over: All ships sunk!'
        return 'Game in progress'

    def visualize_board(self):
        str_rep = ''
        for row in self.board:
            str_rep += ' '.join(row) + '\n'
        print(str_rep)

    def visualize_own_board(self):
        str_rep = ''
        board = self.get_shots_overlay_board()
        for row in board:
            str_rep += ' '.join(row) + '\n'
        print(str_rep)

    def visualize_shots(self):
        str_rep = ''
        for row in self.shots:
            str_rep += ' '.join(row) + '\n'
        print(str_rep)

# Create the board and fill it with ships
# board_width = 10
# board_height = 10
# battleship_board = create_and_fill_battleship_board(board_width, board_height, ships)
#
# # Print the board
# for row in battleship_board:
#     print(' '.join(row))
#
# # Simulating a shot at row 2, column 0 (which should be a hit on 'D1')
# is_hit = check_hit(battleship_board, 2, 0)
#
# print("Hit:", is_hit)
# # Print the updated board to see the result of the shot
# for row in battleship_board:
#     print(' '.join(row))

# Create a Battleship environment
# battleship_env = BattleshipBoard(10, 10, ships)

# Visualize the board and shots
# battleship_env.visualize_board()
# battleship_env.visualize_shots()

# class BattleshipEnv(gymnasium.Env):
#     pass
