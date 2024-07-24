import random
import copy


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
        if num_each_type == 1:
            num_each_type = ship_type_to_num[ship_symbol]

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

ship_type_to_num = {
    'C': 1,
    'B': 1,
    'R': 2,
    'S': 2,
    'D': 2
}


# Define BattleshipBoard class
class BattleshipBoard:
    def __init__(self, width, height, num_each_type=1, exclude_ships=[], init_with_one_hit=False):
        self.width = width
        self.height = height
        self.ships = {s: ships[s] for s in ships if s not in exclude_ships}
        self.board = create_and_fill_battleship_board(width, height, self.ships, num_each_type=num_each_type)
        self.shots = [['.' for _ in range(width)] for _ in range(height)]
        self.hits = 0
        self.misses = 0

        self.ship_positions = {}
        self.get_ship_positions()

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

    def get_ship_positions(self):
        """
        {'C': [(2, 1, True, 'tip'),
          (3, 1, True, 'body'),
          (4, 1, True, 'body'),
          (5, 1, True, 'body'),
          (6, 1, True, 'tail'),
          (5, 8, True, 'tip'),
          (6, 8, True, 'body'),
          (7, 8, True, 'body'),
          (8, 8, True, 'body'),
          (9, 8, True, 'tail')],
         'B': ...}
        """
        if len(self.ship_positions) > 0:
            return

        ship_positions = {}
        visited = [[False for _ in range(self.width)] for _ in range(self.height)]

        for ship_symbol, size in self.ships.items():
            ship_positions[ship_symbol] = []

            for row in range(self.height):
                for col in range(self.width):
                    if self.board[row][col] == ship_symbol and not visited[row][col]:
                        # Determine if the ship is vertical or horizontal
                        is_vertical = False
                        if row + 1 < self.height and self.board[row + 1][col] == ship_symbol:
                            is_vertical = True

                        # Mark the ship parts
                        if is_vertical:
                            for i in range(size):
                                current_row = row + i
                                if current_row < self.height and self.board[current_row][col] == ship_symbol:
                                    part = "body"
                                    if i == 0:
                                        part = "tip"
                                    elif i == size - 1:
                                        part = "tail"
                                    ship_positions[ship_symbol].append((current_row, col, True, part))
                                    visited[current_row][col] = True
                        else:
                            for i in range(size):
                                current_col = col + i
                                if current_col < self.width and self.board[row][current_col] == ship_symbol:
                                    part = "body"
                                    if i == 0:
                                        part = "tip"
                                    elif i == size - 1:
                                        part = "tail"
                                    ship_positions[ship_symbol].append((row, current_col, False, part))
                                    visited[row][current_col] = True

        self.ship_positions = ship_positions

    def check_terminate(self):
        return self.hits == sum(self.ships.values())

    def get_board(self):
        return copy.copy(self.board)

    def get_shots(self):
        return copy.copy(self.shots)

    def get_shots_overlay_board(self):
        shots_overlay_board = [
            [self.board[row][col] if self.shots[row][col] == '.' else self.shots[row][col] for col in range(self.width)]
            for row in range(self.height)]
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

    def render_html(self, show_ships=False):
        from IPython.display import HTML, display

        html = """
        <style>
            table {
                border-collapse: collapse;
                border-radius: 15px;
                overflow: hidden;
                background-color: #699BF7;
                text-align: center;
                margin-bottom: 10px;
            }
            td {
                width: 35px;
                height: 35px;
                text-align: center;
                vertical-align: middle;
                font-weight: bold;
                font-size:13px;
                background-color: #699BF7;
            }

            .header {
                background-color: #699BF7;
            }
            .water {
                background-image: url('https://microsoft.github.io/Trace/images/battleship_widgets/empty.png');
                background-size: cover;
            }
            .hit {
                background-image: url('https://microsoft.github.io/Trace/images/battleship_widgets/hit.png');
                background-size: cover;
            }
            .miss {
                background-image: url('https://microsoft.github.io/Trace/images/battleship_widgets/miss.png');
                background-size: cover;
            }
            .ship-head-horizontal {
                background-image: url('https://microsoft.github.io/Trace/images/battleship_widgets/ship_hl.png');
                background-size: cover;
            }
            .ship-body-horizontal {
                background-image: url('https://microsoft.github.io/Trace/images/battleship_widgets/ship_h.png');
                background-size: cover;
            }
            .ship-tail-horizontal {
                background-image: url('https://microsoft.github.io/Trace/images/battleship_widgets/ship_hr.png');
                background-size: cover;
            }
            .ship-head-vertical {
                background-image: url('https://microsoft.github.io/Trace/images/battleship_widgets/ship_vt.png');
                background-size: cover;
            }
            .ship-body-vertical {
                background-image: url('https://microsoft.github.io/Trace/images/battleship_widgets/ship_v.png');
                background-size: cover;
            }
            .ship-tail-vertical {
                background-image: url('https://microsoft.github.io/Trace/images/battleship_widgets/ship_vb.png');
                background-size: cover;
            }
        </style>
        """

        html += "<table border='1'>\n"

        # Add column headers
        html += "<tr><td class='header'></td>"
        for col in range(self.width):
            html += f"<td class='header'>{chr(65 + col)}</td>"
        html += "<td class='header'></td></tr>\n"  # Extra header cell for the additional column

        # Get ship positions
        ship_positions = self.ship_positions

        for row in range(self.height):
            html += f"<tr><td class='header'>{row + 1}</td>"
            for col in range(self.width):
                cell_class = "water"
                cell_content = "&nbsp;"

                if show_ships and self.board[row][col] != '.':
                    for ship_symbol, positions in ship_positions.items():
                        for position in positions:
                            if position[0] == row and position[1] == col:
                                if position[2]:  # Vertical
                                    if position[3] == 'tip':
                                        cell_class = "ship-head-vertical"
                                    elif position[3] == 'body':
                                        cell_class = "ship-body-vertical"
                                    elif position[3] == 'tail':
                                        cell_class = "ship-tail-vertical"
                                else:  # Horizontal
                                    if position[3] == 'tip':
                                        cell_class = "ship-head-horizontal"
                                    elif position[3] == 'body':
                                        cell_class = "ship-body-horizontal"
                                    elif position[3] == 'tail':
                                        cell_class = "ship-tail-horizontal"
                                cell_content = ship_symbol

                if self.shots[row][col] == 'X':
                    cell_class = "hit"
                    cell_content = ""
                elif self.shots[row][col] == 'O':
                    cell_class = "miss"
                    cell_content = ""

                html += f"<td class='{cell_class}'></td>"

            html += "<td class='header'></td></tr>\n"  # Extra cell for the additional column

        # Add extra row
        html += "<tr><td class='header'></td>"
        for col in range(self.width):
            html += "<td class='header'></td>"
        html += "<td class='header'></td></tr>\n"  # Extra cell for the additional column

        html += "</table>"

        display(HTML(html))
