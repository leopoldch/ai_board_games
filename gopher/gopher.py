"""définition de la classe du jeu gopher"""

import time
import copy
from utils import *
from pers import *
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache


class Gopher_Game:
    """classe du jeu gopher"""

    def verif(self) -> None:
        if not self.__updated:
            self.legit_moves()

    def __init__(self, size: int, starting_player: Player) -> None:
        self.__size = size
        self.__profondeur = 3  # profondeur par défaut
        self.__firstmove = True
        self.__current_player = starting_player
        self.__grid: Grid
        self.create_board()
        self.__updated = False
        self.__legits: list[Cell] = []
        self.__played = []
        self.__starting = starting_player

    def set_player(self, player: Player):
        if player not in [1, 2]:
            raise ValueError("Le joueur doit être soit 1 soit 2")
        self.__current_player = player

    def create_board(self) -> None:
        """create board using a size"""
        sizet = self.__size * 2 - 1

        self.__grid: dict[Cell:Player] = {}
        counter: int = math.ceil(sizet / 2)
        start = [0, math.floor(sizet / 2)]
        verif: bool = True
        iterations: int = sizet
        if sizet % 2 == 0:
            iterations += 1
        for _ in range(iterations):
            if counter == sizet:
                verif = False
            if verif:
                for i in range(counter):
                    cell: Cell = (start[0] + i, start[1])
                    self.__grid[cell] = 0
                counter += 1
                start = [start[0] - 1, start[1] - 1]
            else:
                for i in range(counter):
                    cell: Cell = (start[0] + i, start[1])
                    self.__grid[cell] = 0
                counter -= 1
                start = [start[0], start[1] - 1]

    def __str__(self) -> str:
        """prints the board"""
        sizet: int = self.__size * 2 - 1
        returned_str: str = ""
        counter: int = math.ceil(sizet / 2)
        start = [0, math.floor(sizet / 2)]
        verif: bool = True
        iterations: int = sizet
        if sizet % 2 == 0:
            iterations += 1
        for _ in range(iterations):
            if counter == sizet:
                verif = False
            if verif:
                returned_str += " " * (sizet - counter)
                for i in range(counter):
                    cell: Cell = (start[0] + i, start[1])
                    case: int = self.__grid[cell]
                    if case == 1:
                        tmp: str = str_red("X")
                        returned_str += f"{tmp} "
                    elif case == 2:
                        tmp: str = str_blue("O")
                        returned_str += f"{tmp} "
                    else:
                        returned_str += "* "
                returned_str += "\n"
                counter += 1
                start = [start[0] - 1, start[1] - 1]
            else:
                returned_str += " " * (sizet - counter)
                for i in range(counter):
                    cell: Cell = (start[0] + i, start[1])
                    case: int = self.__grid[cell]
                    if case == 1:
                        tmp: str = str_red("X")
                        returned_str += f"{tmp} "
                    elif case == 2:
                        tmp: str = str_blue("O")
                        returned_str += f"{tmp} "
                    else:
                        returned_str += "* "
                returned_str += "\n"
                counter -= 1
                start = [start[0], start[1] - 1]
        return returned_str

    def copy(self):
        """Retourne une copie de l'objet Gopher_Game"""
        new_game = Gopher_Game(self.__size, self.__current_player)
        new_game.__grid = self.__grid.copy()
        new_game.__firstmove = self.__firstmove
        new_game.__updated = self.__updated
        new_game.__legits = self.__legits.copy()
        new_game.__played = self.__played.copy()
        new_game.__starting = self.__starting
        new_game.__profondeur = self.__profondeur
        return new_game

    def get_neighbors(self, x: int, y: int) -> list[Cell]:
        max_val = self.__size - 1
        if abs(x) > max_val or abs(y) > max_val:
            raise ValueError("Case non dans le tableau")
        neighbors = []
        for dx, dy in [(-1, -1), (-1, 0), (0, -1), (0, 1), (1, 0), (1, 1)]:
            vx, vy = x + dx, y + dy
            if (-max_val <= vx <= max_val) and (-max_val <= vy <= max_val):
                key = (vx, vy)
                if key in self.__grid and self.__grid[key] != -1:
                    neighbors.append(key)
        return neighbors

    def calculate_strategic_positions(self) -> list[Cell]:
        """Calculates strategic positions based on the size of the grid."""
        strategic_positions = []
        max_distance = self.__size - 1
        center = (0, 0)

        strategic_positions.append(center)

        adjacent_positions = self.get_neighbors(center[0], center[1])
        strategic_positions.extend(adjacent_positions)

        for x in range(-max_distance, max_distance + 1):
            for y in range(-max_distance, max_distance + 1):
                if (
                    x == -max_distance
                    or x == max_distance
                    or y == -max_distance
                    or y == max_distance
                ):
                    cell = (x, y)
                    if cell in self.__grid.keys():
                        strategic_positions.append(cell)

        return strategic_positions

    def is_strategic_position(self, cell: Cell) -> bool:
        """Check if the cell is in a strategic position."""
        strategic_positions = self.calculate_strategic_positions()
        return cell in strategic_positions

    def evaluate(self, cell: Cell) -> float:
        """Evaluate the potential of a move."""
        score = 0
        self.legit_moves()

        # Check if the move is at the center
        if cell == (0, 0):
            score += 5

        # Check if the move is in a strategic position
        if self.is_strategic_position(cell):
            score += 3

        # Evaluate potential future moves
        future_moves = len(self.__legits)
        score += future_moves

        return score

    def is_legit(self, start: Cell) -> bool:
        """returns if move is legit or not"""
        if self.__firstmove:
            return True
        if start == None:
            return False
        if self.__grid[start] != 0:
            return False

        neighbors: list[Cell] = self.get_neighbors(start[0], start[1])
        verif: int = 0
        for item in neighbors:
            if verif > 1:
                return False
            if self.__grid[(item[0], item[1])] == self.__current_player:
                return False
            if self.__current_player == 1:
                if self.__grid[(item[0], item[1])] == 2:
                    verif += 1
            elif self.__current_player == 2:
                if self.__grid[(item[0], item[1])] == 1:
                    verif += 1
        if verif == 1:
            return True
        return False

    def legit_moves(self) -> None:
        """returns legit moves in game"""
        if not self.__updated:
            if self.__firstmove:
                self.__legits = list(self.__grid.keys())
            for item in self.__grid.items():
                if item[1] == 0 and self.is_legit(item[0]):
                    self.__legits.append(item[0])
            self.__updated = True

    def move(self, cell: Cell) -> None:
        """play item on grid"""
        if not self.is_legit(cell):
            raise ValueError("Impossible de bouger ce pion à cet endroit")
        else:
            if self.__firstmove:
                self.__firstmove = False
            self.__grid[cell] = self.__current_player
            self.__updated = False
            self.__legits = []
            self.__played.append(cell)

    def score(self) -> float:
        """evaluation func"""
        self.verif()
        if self.__firstmove:
            return 1
        if self.__legits:
            return 1
        else:
            return -1

        """evaluation func"""
        v: bool = False
        if self.__current_player == 2:
            self.set_player(1)
            v = True
        if self.__firstmove:
            if v:
                self.set_player(1)
            return 1
        if self.__legits:
            if v:
                self.set_player(1)
            return 1
        else:
            if v:
                self.set_player(1)
            return -1

    def final(self) -> bool:
        """returns if game has ended"""
        self.verif()
        if self.__legits:
            return True
        return False

    @memoize
    def minmax_action(self, depth: int = 0) -> tuple[float, Action]:
        """Minimax function with memoization."""
        best: tuple[float, Action] = (None, None)
        self.verif()

        if depth == 0 or not self.__legits:
            return (self.score(), None)

        original_grid = self.__grid.copy()  # Faire une copie de la grille initiale

        if self.__current_player == 1:
            best_value = float("-inf")
            for move in self.__legits:
                self.move(move)
                self.set_player(2)
                score, _ = self.minmax_action(depth - 1)
                move_score = self.evaluate(move)
                total_score = score + move_score
                if total_score > best_value:
                    best_value = total_score
                    best = (total_score, move)
                self.__grid = original_grid.copy()  # Restaurer la grille initiale
                self.set_player(1)
            return best

        if self.__current_player == 2:
            best_value = float("inf")
            for move in self.__legits:
                self.move(move)
                self.set_player(1)
                score, _ = self.minmax_action(depth - 1)
                move_score = self.evaluate(move)
                total_score = score + move_score
                if total_score < best_value:
                    best_value = total_score
                    best = (total_score, move)
                self.__grid = original_grid.copy()  # Restaurer la grille initiale
                self.set_player(2)
            return best

        raise ValueError("Joueur inconnu")

    def strategy_minmax(self) -> Action:
        """strategy de jeu avec minmax"""
        length: int = len(self.__played)
        if self.__firstmove and self.__size % 2 == 1:
            return (0, 0)
        elif self.__firstmove and self.__size % 2 == 0:
            return (0, self.__size - 1)
        elif (
            length > 1
            and self.__starting == self.__current_player
            and self.__size % 2 == 1
        ):
            length -= 1
            next_cell: Cell = self.get_direction()
            if next_cell in self.__legits:
                return next_cell
        value: Action = self.minmax_action(self.__profondeur)[1]
        return value

    def alpha_beta_action(
        self, depth: int = 0, alpha: float = float("-inf"), beta: float = float("inf")
    ) -> tuple[float, Action]:
        """Alpha-beta pruning function using evaluate for move evaluation."""
        self.verif()
        best: tuple[float, Action] = (None, None)

        if depth == 0 or not self.__legits:
            return (self.score(), None)

        original_grid = self.__grid.copy()  # Faire une copie de la grille initiale

        if self.__current_player == 1:
            best_value = float("-inf")
            for move in self.__legits:
                self.move(move)
                self.set_player(2)
                score, _ = self.alpha_beta_action(depth - 1, best_value, beta)
                # Use evaluate to assess the move
                move_score = self.evaluate(move)
                total_score = score + move_score
                if total_score > best_value:
                    best_value = total_score
                    best = (total_score, move)
                self.__grid = original_grid.copy()  # Restaurer la grille initiale
                self.set_player(1)
                if best_value >= beta:
                    break  # Coupure bêta
            return best

        if self.__current_player == 2:
            best_value = float("inf")
            for move in self.__legits:
                self.move(move)
                self.set_player(1)
                score, _ = self.alpha_beta_action(depth - 1, alpha, best_value)
                # Use evaluate to assess the move
                move_score = self.evaluate(move)
                total_score = score + move_score
                if total_score < best_value:
                    best_value = total_score
                    best = (total_score, move)
                self.__grid = original_grid.copy()  # Restaurer la grille initiale
                self.set_player(2)
                if best_value <= alpha:
                    break  # Coupure alpha
            return best

        raise ValueError("Joueur inconnu")

    def alpha_beta_action_parallel(
        self, depth: int = 0, alpha: float = float("-inf"), beta: float = float("inf")
    ) -> tuple[float, Action]:
        """Alpha-beta pruning with parallel processing."""
        self.verif()
        best: tuple[float, Action] = (None, None)

        if depth == 0 or not self.__legits:
            return (self.score(), None)

        def evaluate_move(move):
            temp_game = self.copy()
            temp_game.move(move)
            temp_game.set_player(3 - temp_game.__current_player)
            score, _ = temp_game.alpha_beta_action(depth - 1, alpha, beta)
            move_score = temp_game.evaluate(move)
            total_score = score + move_score
            return total_score, move

        with ThreadPoolExecutor() as executor:
            future_to_move = {
                executor.submit(evaluate_move, move): move for move in self.__legits
            }
            results = []

            for future in as_completed(future_to_move):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    print(f"Generated an exception: {exc}")

        if self.__current_player == 1:
            best = max(results, key=lambda x: x[0])
        else:
            best = min(results, key=lambda x: x[0])

        return best

    def strategy_alpha_beta(self) -> Action:
        """Strategy de jeu avec alpha-beta"""
        length: int = len(self.__played)

        if self.__firstmove:
            if self.__size % 2 == 1:
                return (0, 0)
            else:
                return (0, self.__size - 1)
        elif (
            length > 1
            and self.__starting == self.__current_player
            and self.__size % 2 == 1
        ):
            length -= 1
            next_cell: Cell = self.get_direction()
            if next_cell in self.__legits:
                return next_cell

        value: Action = self.alpha_beta_action(self.__profondeur)[1]
        return value

    def strategy_mcts(self) -> Action:
        length = len(self.__played)
        if self.__firstmove and self.__size % 2 == 1:
            return (0, 0)
        elif self.__firstmove and self.__size % 2 == 0:
            return (0, self.__size - 1)
        elif (
            length > 1
            and self.__starting == self.__current_player
            and self.__size % 2 == 1
        ):
            length -= 1
            next_cell = self.get_direction()
            if next_cell in self.__legits:
                return next_cell
        return mcts(self)

    def strategy_random(self) -> Action:
        """function to play with a random strat"""
        self.verif()
        value = random.randint(0, len(self.__legits) - 1)
        return self.__legits[value]

    def negamax(self, depth: int, alpha: float, beta: float, player: int) -> float:
        """Négamax avec élagage alpha-beta."""
        self.verif()
        if depth == 0 or not self.__legits:
            return self.evaluate_negamax(player)

        max_eval = float("-inf")
        original_grid = self.__grid.copy()

        for move in self.__legits:
            self.move(move)
            self.set_player(3 - self.__current_player)
            eval = -self.negamax(depth - 1, -beta, -alpha, 3 - player)
            self.__grid = original_grid.copy()
            self.set_player(player)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if alpha >= beta:
                break

        return max_eval

    def evaluate_negamax(self, player: int) -> float:
        """Fonction d'évaluation pour le Négamax."""
        return self.score() if self.__current_player == player else -self.score()

    def negamax_action(self, depth: int = 3) -> tuple[float, Cell]:
        """Trouve le meilleur mouvement en utilisant Négamax."""
        best_move = None
        max_eval = float("-inf")
        alpha = float("-inf")
        beta = float("inf")

        original_grid = self.__grid.copy()
        player = self.__current_player

        for move in self.__legits:
            self.move(move)
            self.set_player(3 - self.__current_player)
            eval = -self.negamax(depth - 1, -beta, -alpha, 3 - player)
            self.__grid = original_grid.copy()
            self.set_player(player)
            if eval > max_eval:
                max_eval = eval
                best_move = move

        return max_eval, best_move

    def strategy_negamax(self) -> Cell:
        """Stratégie de jeu utilisant Négamax."""
        length = len(self.__played)
        if self.__firstmove and self.__size % 2 == 1:
            return (0, 0)
        elif self.__firstmove and self.__size % 2 == 0:
            return (0, self.__size - 1)
        elif (
            length > 1
            and self.__starting == self.__current_player
            and self.__size % 2 == 1
        ):
            length -= 1
            next_cell = self.get_direction()
            if next_cell in self.__legits:
                return next_cell
        value = self.negamax_action(self.__profondeur)[1]
        return value

    def update_grid_from_state(self, state: State) -> None:
        self.__grid = state_to_grid(state)

    def get_state_from_grid(self) -> State:
        return grid_to_state(self.__grid)

    def get_grid(self) -> Grid:
        return self.__grid

    def set_grid(self, newgrid: Grid) -> None:
        self.__grid = newgrid

    def set_depth(self, depth: int) -> None:
        if depth <= 0:
            raise ValueError("Profondeur incorrecte")
        self.__profondeur = depth

    def get_player(self) -> Player:
        """getter pour l'attribut joueur"""
        return self.__current_player

    def get_legits(self) -> list[Cell]:
        """getter pour l'attrbut legit"""
        self.verif()
        return self.__legits

    def get_direction(self) -> Cell:
        last: Cell = self.__played[-1]
        value = self.__grid[last]
        verif = 0
        aligned = None
        for tup in self.get_neighbors(last[0], last[1]):
            if self.__grid[tup] == 3 - value:
                # un seul résultat
                verif += 1
                aligned = tup
        if verif > 1 or verif == 0:
            raise ValueError("Incohérence dans le jeu")
        dx: int = last[0] - aligned[0]
        dy: int = last[1] - aligned[1]
        next_cell = (last[0] + dx, last[1] + dy)
        return next_cell

    def save_state(self) -> dict:
        """Sauvegarde l'état actuel du jeu sous forme de dictionnaire."""
        return {
            "grid": self.__grid.copy(),
            "current_player": self.__current_player,
            "firstmove": self.__firstmove,
            "size": self.__size,
            "legits": self.__legits,
            "played": self.__played,
            "starting": self.__starting,
            "updated": self.__updated,
        }

    def restore_state(self, state: dict) -> None:
        """Restaure l'état du jeu à partir d'un dictionnaire."""
        self.__grid = state["grid"]
        self.__current_player = state["current_player"]
        self.__firstmove = state["firstmove"]
        self.__size = state["size"]
        self.__legits = state["legits"]
        self.__played = state["played"]
        self.__starting = state["starting"]
        self.__updated = state["updated"]
