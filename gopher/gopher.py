"""définition de la classe du jeu gopher"""

# Dear programmer
# When I wrote this code, only god and
# I knew how it worked.
# Now, only god know it !

# Therefore, if you are trying to optimize
# the strategies and it fails (most surely),
# please increase this counter as a
# warning for the next person

# total_hours_wated_here = 254

import math
import random
from typing import Optional
from gopher.utils import (
    Action,
    state_to_grid,
    str_blue,
    str_red,
    Cell,
    Player,
    State,
    Grid,
    Environment,
)
from gopher.mcts_class import mcts


class GopherGame:
    """classe du jeu gopher"""

    # --- FONCTIONS UTILITAIRES POUR LE FONCTIONNEMENT DU JEU ---

    def __init__(self, size: int, starting_player: Player) -> None:
        """constructeur de Gopher"""
        self.__size: int = size
        self.__firstmove: bool = True
        self.__first_visit: bool = True
        self.__current_player: Player = starting_player
        self.__grid: Grid = {}
        self.__create_board()
        self.__updated: bool = False
        self.__legits: list[Cell] = []
        self.__played: list[Cell] = []
        self.__starting: Player = starting_player

    def __create_board(self) -> None:
        """create board using a size"""
        sizet = self.__size * 2 - 1
        counter: int = math.ceil(sizet / 2)
        start = [0, math.floor(sizet / 2)]
        verif: bool = True
        iterations: int = sizet
        cell: Cell
        if sizet % 2 == 0:
            iterations += 1
        for _ in range(iterations):
            if counter == sizet:
                verif = False
            if verif:
                for i in range(counter):
                    cell = (start[0] + i, start[1])
                    self.__grid[cell] = 0
                counter += 1
                start = [start[0] - 1, start[1] - 1]
            else:
                for i in range(counter):
                    cell = (start[0] + i, start[1])
                    self.__grid[cell] = 0
                counter -= 1
                start = [start[0], start[1] - 1]

    def __str__(self) -> str:
        """Prints the board"""
        sizet: int = self.__size * 2 - 1
        returned_str: str = ""
        counter: int = math.ceil(sizet / 2)
        start = [0, math.floor(sizet / 2)]
        iterations: int = sizet + 1 if sizet % 2 == 0 else sizet
        verif: bool = True
        for _ in range(iterations):
            if counter == sizet:
                verif = False

            returned_str += " " * (sizet - counter)
            for i in range(counter):
                cell: Cell = (start[0] + i, start[1])
                case: int = self.__grid[cell]
                if case == 1:
                    returned_str += f"{str_red('X')} "
                elif case == 2:
                    returned_str += f"{str_blue('O')} "
                else:
                    returned_str += "* "
            returned_str += "\n"

            if verif:
                counter += 1
                start = [start[0] - 1, start[1] - 1]
            else:
                counter -= 1
                start = [start[0], start[1] - 1]

        return returned_str

    def __verify_update(self) -> None:
        """vérifier si les coups légits ont été mis à jour"""
        if len(self.__played) > 0:
            self.__firstmove = False
            self.__legits = []
            self.__updated = False
        if not self.__updated:
            self.__legit_moves()

    def __get_neighbors(self, x: int, y: int) -> list[Cell]:
        """récupérer les voisins"""
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

    def __evaluate(self, _) -> float:
        """Evaluate the potential of a move."""
        score = 0
        self.__legit_moves()
        if len(self.get_legits()) == 0:
            score = 100
        elif len(self.get_legits()) == 1:
            score = 50
        else:
            future_moves = len(self.get_legits())
            if future_moves > 3:
                score += 1
            elif future_moves == 3:
                score += 2
            else:
                score += 3
        return -score

    def is_legit(self, start: Cell) -> bool:
        """returns if move is legit or not"""
        if self.__firstmove:
            return True
        if start is None or self.__grid[start] != 0:
            return False
        neighbors: list[Cell] = self.__get_neighbors(start[0], start[1])
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

    def __legit_moves(self) -> None:
        """returns legit moves in game"""
        if not self.__updated:
            if self.__firstmove:
                self.__legits = list(self.__grid.keys())
            for item in self.__grid.items():
                if item[1] == 0 and self.is_legit(item[0]):
                    self.__legits.append(item[0])
            self.__updated = True

    def make_move(self, cell: Cell) -> None:
        """play item on grid"""
        if not self.is_legit(cell):
            raise ValueError("Impossible de bouger ce pion à cet endroit")
        if self.__firstmove:
            self.__firstmove = False
        self.__grid[cell] = self.__current_player
        self.__updated = False
        self.__legits = []
        self.__played.append(cell)

    def score(self) -> float:
        """evaluation func"""
        self.__verify_update()
        if self.__firstmove:
            return 1
        if self.__legits:
            return 1
        return -1

    def final(self) -> bool:
        """returns if game has ended"""
        self.__verify_update()
        if self.__legits:
            return True
        return False

    # ----------------------- ALGO MIN-MAX -----------------------

    # @memoize ralenti
    def __minmax_action(self, depth: int = 0) -> tuple[float, Action]:
        """Minimax func."""
        best: tuple[float, Action]
        self.__verify_update()

        if depth == 0 or not self.__legits:
            return (
                self.score(),
                (-100, -100),
            )  # on admet qu'il n'y a pas de case (-100,-100) dans une grille

        original_grid = self.__grid.copy()  # Copie la grid départ

        if self.__current_player == 1:
            best_value = float("-inf")
            for move in self.__legits:
                self.make_move(move)
                self.set_player(2)
                score, _ = self.__minmax_action(depth - 1)
                move_score = self.__evaluate(move)
                total_score = score + move_score
                if total_score > best_value:
                    best_value = total_score
                    best = (total_score, move)
                self.__grid = original_grid.copy()  # Remet la grid départ
                self.set_player(1)
            return best

        if self.__current_player == 2:
            best_value = float("inf")
            for move in self.__legits:
                self.make_move(move)
                self.set_player(1)
                score, _ = self.__minmax_action(depth - 1)
                move_score = self.__evaluate(move)
                total_score = score + move_score
                if total_score < best_value:
                    best_value = total_score
                    best = (total_score, move)
                self.__grid = original_grid.copy()  # Remet la grid départ
                self.set_player(2)
            return best

        raise ValueError("Joueur inconnu")

    # --------------------- ALGO ALPHA-BETA ----------------------

    def __alpha_beta_action(
        self, depth: int = 0, alpha: float = float("-inf"), beta: float = float("inf")
    ) -> tuple[float, Action]:
        """Alpha-beta func"""
        self.__verify_update()
        best: tuple[float, Action]

        if depth == 0 or not self.__legits:
            return (
                self.score(),
                (-100, -100),
            )  # on admet qu'il n'y a pas de case (-100,-100) dans une grille

        original_grid = self.__grid.copy()  # Copie la grid départ

        if self.__current_player == 1:
            best_value = float("-inf")
            for move in self.__legits:
                self.make_move(move)
                self.set_player(2)
                score, _ = self.__alpha_beta_action(depth - 1, best_value, beta)
                # Use evaluate to assess the move
                move_score = self.__evaluate(move)
                total_score = score + move_score
                if total_score > best_value:
                    best_value = total_score
                    best = (total_score, move)
                self.__grid = original_grid.copy()  # Remet la grid départ
                self.set_player(1)
                if best_value >= beta:
                    break  # Coupure bêta
            return best

        if self.__current_player == 2:
            best_value = float("inf")
            for move in self.__legits:
                self.make_move(move)
                self.set_player(1)
                score, _ = self.__alpha_beta_action(depth - 1, alpha, best_value)
                move_score = self.__evaluate(move)
                total_score = score + move_score
                if total_score < best_value:
                    best_value = total_score
                    best = (total_score, move)
                self.__grid = original_grid.copy()  # Remet la grid départ
                self.set_player(2)
                if best_value <= alpha:
                    break  # Coupure alpha
            return best

        raise ValueError("Joueur inconnu")

    # ----------------------- ALGO NEGAMAX -----------------------

    def __negamax_depth(self) -> int:
        """depth for negamax"""
        n: int = sum(
            1 for value in self.__grid.values() if value == 0
        )  # Attention O(n)
        value = 3
        if 217 < n <= 269:
            value = 4
        if 127 < n <= 217:
            value = 7
        if 91 < n <= 127:
            value = 7
        if 37 < n <= 91:
            value = 9
        if 19 < n <= 37:
            value = 10
        return value

        # if self.__size <= 3: return 12
        # depths : dict[int,int] = {4:11,5:9,6:9,7:7,8:6,9:6,10:4}
        # return depths[self.__size]

    def __negamax(self, depth: int, alpha: float, beta: float, player: int) -> float:
        """Négamax avec élagage alpha-beta."""
        self.__verify_update()

        if depth == 0 or not self.__legits:
            return self.__evaluate_negamax(player)

        max_eval = float("-inf")
        original_grid = self.__grid.copy()
        ordered_moves = sorted(
            self.__legits, key=self.__evaluate, reverse=True
        )  # Tri heuristique

        for move in ordered_moves:
            self.make_move(move)
            self.set_player(3 - self.__current_player)
            eval_value = -self.__negamax(depth - 1, -beta, -alpha, 3 - player)
            self.__grid = original_grid.copy()
            self.set_player(player)
            max_eval = max(max_eval, eval_value)
            alpha = max(alpha, eval_value)
            if alpha >= beta:
                break
        return max_eval

    def __negamax_action(self, depth: int = 3) -> tuple[float, Cell]:
        """Trouve le meilleur mouvement en utilisant Négamax."""
        best_move: tuple[int, int]
        max_eval = float("-inf")
        alpha = float("-inf")
        beta = float("inf")

        original_grid = self.__grid.copy()
        player = self.__current_player
        ordered_moves = sorted(self.__legits, key=self.__evaluate, reverse=True)
        for move in ordered_moves:
            self.make_move(move)
            self.set_player(3 - self.__current_player)
            eval_value = -self.__negamax(depth - 1, -beta, -alpha, 3 - player)
            self.__grid = original_grid.copy()
            self.set_player(player)
            if eval_value > max_eval:
                max_eval = eval_value
                best_move = move

        return max_eval, best_move

    def __evaluate_negamax(self, player: int) -> float:
        """Fonction d'évaluation pour le Négamax."""
        return self.score() if self.__current_player == player else -self.score()

    # ---------------- DEFINITION DES STRATÉGIES ----------------

    def strategy_negamax(self) -> Action:
        """Stratégie de jeu utilisant Négamax."""
        length = len(self.__played)
        if self.__firstmove and self.__size % 2 == 1:
            return (0, 0)
        if self.__firstmove and self.__size % 2 == 0:
            return (0, self.__size - 1)
        if (
            length > 1
            and self.__starting == self.__current_player
            and self.__size % 2 == 1
        ):
            length -= 1
            next_cell = self.get_direction()
            if next_cell in self.__legits:
                return next_cell
        depth: int = self.__negamax_depth()
        tmp: list[Cell] = self.__played.copy()
        value = self.__negamax_action(depth)[1]
        self.__played = tmp
        return value

    def strategy_random(self) -> Action:
        """function to play with a random strat"""
        self.__verify_update()
        if len(self.__legits) == 0:
            raise ValueError("Attention plus d'action possibles")
        value = random.randint(0, len(self.__legits) - 1)
        return self.__legits[value]

    def strategy_minmax(self) -> Action:
        """strategy de jeu avec minmax"""
        length: int = len(self.__played)
        if self.__firstmove and self.__size % 2 == 1:
            return (0, 0)
        if self.__firstmove and self.__size % 2 == 0:
            return (0, self.__size - 1)
        if (
            length > 1
            and self.__starting == self.__current_player
            and self.__size % 2 == 1
        ):
            length -= 1
            next_cell: Cell = self.get_direction()
            if next_cell in self.__legits:
                return next_cell
        tmp: list[Cell] = self.__played.copy()
        value: Action = self.__minmax_action(3)[1]
        self.__played = tmp
        return value

    def strategy_mcts(self) -> Optional[Action]:
        """stratégie MCTS"""
        length = len(self.__played)
        if self.__firstmove and self.__size % 2 == 1:
            return (0, 0)
        if self.__firstmove and self.__size % 2 == 0:
            return (0, self.__size - 1)
        if (
            length > 1
            and self.__starting == self.__current_player
            and self.__size % 2 == 1
        ):
            length -= 1
            next_cell = self.get_direction()
            if next_cell in self.__legits:
                return next_cell
        tmp: list[Cell] = self.__played.copy()
        value: Optional[Action] = mcts(self)
        self.__played = tmp
        return value

    def strategy_alpha_beta(self) -> Action:
        """Strategy de jeu avec alpha-beta"""
        length: int = len(self.__played)

        if self.__firstmove:
            if self.__size % 2 == 1:
                return (0, 0)
            return (0, self.__size - 1)
        if (
            length > 1
            and self.__starting == self.__current_player
            and self.__size % 2 == 1
        ):
            length -= 1
            next_cell: Cell = self.get_direction()
            if next_cell in self.__legits:
                return next_cell
        tmp_played: list[Cell] = self.__played.copy()
        value: Action = self.__alpha_beta_action(3)[1]
        self.__played = tmp_played
        return value

    # ---------------- GETTER ET SETTERS PUBLICS ----------------

    def get_grid(self) -> Grid:
        """getter de la grid"""
        return self.__grid

    def set_grid(self, newgrid: Grid) -> None:
        """setter de la grid"""
        self.__grid = newgrid

    def get_player(self) -> Player:
        """getter pour l'attribut joueur actuel"""
        return self.__current_player

    def set_player(self, player: Player):
        """Setter pour le joueur actuel"""
        if player not in [1, 2]:
            raise ValueError("Le joueur doit être soit 1 soit 2")
        self.__current_player = player

    def get_legits(self) -> list[Cell]:
        """getter pour l'attrbut legit"""
        self.__verify_update()
        return self.__legits

    def get_played(self) -> list[Cell]:
        """retourne les coups joués"""
        return self.__played

    def get_direction(self) -> Cell:
        """fonction pour avoir la direction en cas de grille impair"""
        last: Cell = self.__played[-1]
        value = self.__grid[last]
        verif = 0
        aligned: tuple[int, int]
        for tup in self.__get_neighbors(last[0], last[1]):
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
            "first_visit": self.__first_visit,
        }

    def restore_state(self, state: dict) -> None:
        """Permet de remettres des attributs utile dans MCTS"""
        self.__grid = state["grid"]
        self.__current_player = state["current_player"]
        self.__firstmove = state["firstmove"]
        self.__size = state["size"]
        self.__legits = state["legits"]
        self.__played = state["played"]
        self.__starting = state["starting"]
        self.__updated = state["updated"]
        self.__first_visit = state["first_visit"]

    def to_environnement(self) -> dict:
        """Sauvegarde l'état actuel du jeu sous forme de dictionnaire."""
        return {
            "grid": self.__grid.copy(),
            "current_player": self.__current_player,
            "firstmove": self.__firstmove,
            "size": self.__size,
            "legits": self.__legits,
            "played": self.__played,
            "starting": self.__starting,
            "updated": False,
            "game": "gopher",
            "first_visit": self.__first_visit,
        }

    def restore_env(self, state: State, env: Environment, current: Player) -> None:
        """permet de restaurer le jeu à partir de l'environnement"""

        self.restore_state(
            env
        )  # attention on restaure avec l'ancienne grille volontairement
        opponent: Player = 3 - current
        self.__current_player = current
        self.__updated = False
        new_grid: Grid = state_to_grid(state)
        if new_grid != self.__grid:
            for key, item in new_grid.items():
                if (
                    self.__grid[key] == 0 and item == opponent
                ):  # on a trouvé le dernier coup
                    self.__played.append(key)
        self.__grid = new_grid

        if self.__first_visit:
            if len(self.__played) == 1:
                self.__starting = opponent
                self.__firstmove = False
                self.__legits = []
            elif len(self.__played) == 0:
                self.__starting = current
        self.__verify_update()
