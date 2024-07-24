import random

def create_battleship_board(width, height):
    board = [['.' for _ in range(width)] for _ in range(height)]
    return board

def can_place_ship(board, row, col, size, is_vertical):
    if is_vertical:
        if row + size > len(board):
            return False
        for i in range(size):
            if board[row + i][col] != '.':
                return False
    else:
        if col + size > len(board[0]):
            return False
        for i in range(size):
            if board[row][col + i] != '.':
                return False
    return True

def place_ship(board, row, col, size, is_vertical, ship_symbol):
    if is_vertical:
        for i in range(size):
            board[row + i][col] = ship_symbol
    else:
        for i in range(size):
            board[row][col + i] = ship_symbol

def create_and_fill_battleship_board(width, height, ships, num_each_type=2):
    board = [['.' for _ in range(width)] for _ in range(height)]
    for ship_symbol, size in ships.items():
        for num in range(1, num_each_type + 1):
            placed = False
            while not placed:
                row = random.randint(0, height - 1)
                col = random.randint(0, width - 1)
                is_vertical = random.choice([True, False])
                if can_place_ship(board, row, col, size, is_vertical):
                    place_ship(board, row, col, size, is_vertical, ship_symbol)
                    placed = True
    return board

def check_hit(board, row, col):
    if 0 <= row < len(board) and 0 <= col < len(board[0]):
        if board[row][col] not in ['.', 'O', 'X']:
            board[row][col] = 'X'
            return True
        else:
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

# Define BattleshipBoard class
class BattleshipBoard:
    def __init__(self, width, height, num_each_type=2, exclude_ships=[], init_with_one_hit=False):
        self.width = width
        self.height = height
        self.ships = {s: ships[s] for s in ships if s not in exclude_ships}
        self.board = create_and_fill_battleship_board(width, height, self.ships, num_each_type=num_each_type)
        self.shots = [['.' for _ in range(width)] for _ in range(height)]
        self.hits = 0
        self.misses = 0

        if init_with_one_hit:
            initialized = False
            for row in range(height):
                for col in range(width):
                    if self.board[row][col] != '.':
                        self.check_shot(row, col)
                        initialized = True
                        break
                if initialized:
                    break

    def get_life_points(self):
        return sum(self.ships.values())

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