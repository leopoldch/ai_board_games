import random
import math
from dodo.utils import (
    Action,
    state_to_grid,
    str_blue,
    str_red,
    Cell,
    Player,
    State,
    Grid,
    Environment,
    get_state_negamax,
)
from collections import deque
from dodo.mcts import mcts

class DodoGame:
    """classe du jeu dodo"""

    def __init__(self, size: int, starting_player: Player) -> None:
        """constructeur de dodo"""
        self.__size: int = size
        self.__firstmove: bool = True
        self.__first_visit: bool = True
        self.__current_player: Player = starting_player
        self.__grid: Grid = {}
        self.__create_board()
        self.__updated: bool = False
        self.__legits: list[tuple[Cell, Cell]] = []
        self.__played: list[tuple[Cell, Cell]] = []
        self.__starting: Player = starting_player
        self.__negamax_cache: dict = {}

    def copy(self):
        """constructeur de dodo"""
        new_game = DodoGame(self.__size,self.__current_player)
        new_game.__firstmove = self.__firstmove
        new_game.__first_visit = self.__first_visit
        new_game.__current_player = self.__current_player
        new_game.__grid = self.__grid.copy()
        new_game.__updated = self.__updated
        new_game.__legits = self.__legits.copy()
        new_game.__played = self.__played.copy()
        new_game.__starting = self.__starting
        return new_game

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

        """Checkers placement"""
        size = self.__size
        top = (0, size - 1)
        bot = (-(size - 1), 0)

        for i in range(size):
            top_pos = (top[0], top[1])
            bot_pos = (bot[0], bot[1])

            for _ in range(size - i):
                self.__grid[top_pos] = 2
                self.__grid[bot_pos] = 1
                top_pos = (top_pos[0] + 1, top_pos[1] - 1)
                bot_pos = (bot_pos[0] + 1, bot_pos[1] - 1)

            top = (top[0] + 1, top[1])
            bot = (bot[0], bot[1] - 1)
        line_bot = (-(size - 2), 0)
        line_top = (0, size - 2)
        for i in range(size - 1):
            self.__grid[line_top] = 2
            self.__grid[line_bot] = 1
            line_top = (line_top[0] + 1, line_top[1] - 1)
            line_bot = (line_bot[0] + 1, line_bot[1] - 1)

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
        if self.__played:
            self.__firstmove = False
            self.__legits = []
            self.__updated = False
        if not self.__updated:
            self.__legit_moves()

    def is_legit(self, action: tuple[Cell, Cell]) -> bool:
        """returns if move is legit or not"""
        if self.__grid[action[0]] != self.__current_player or self.__grid[action[1]] != 0:
            return False

        if self.__current_player == 1:
            directions = [(1, 0), (1, 1), (0, 1)]
        elif self.__current_player == 2:
            directions = [(-1, 0), (-1, -1), (0, -1)]

        cellules_possibles = [(action[0][0] + direction[0], action[0][1] + direction[1]) for direction in directions]
        return action[1] in self.__grid and action[1] in cellules_possibles

    def __legit_moves(self) -> None:
        """returns legit moves in game"""
        if not self.__updated:
            player = self.__current_player
            if player == 1:
                directions = [(1, 0), (1, 1), (0, 1)]
            elif player == 2:
                directions = [(-1, 0), (-1, -1), (0, -1)]
            for cellule, occupant in self.__grid.items():
                if occupant == player:
                    for direction in directions:
                        nouvelle_cellule = (cellule[0] + direction[0], cellule[1] + direction[1])
                        if nouvelle_cellule in self.__grid and self.__grid[nouvelle_cellule] == 0:
                            self.__legits.append((cellule, nouvelle_cellule))
            self.__updated = True

    def make_move(self, action: tuple[Cell, Cell]) -> None:
        """play item on grid"""
        if not self.is_legit(action):
            raise ValueError("Impossible de bouger ce pion à cet endroit")
        if self.__firstmove:
            self.__firstmove = False
        start_cell, end_cell = action
        self.__grid[start_cell] = 0  # on enleve le pion de la position de départ
        self.__grid[end_cell] = self.__current_player # on place le pion dans la position d'arrivée
        self.__updated = False
        self.__legits = []
        self.__played.append(action)

    def unmake_move(self, action: tuple[Cell, Cell]) -> None:
        '''unplay item on grid'''
        start_cell, end_cell = action
        self.__grid[end_cell] = 0
        self.__grid[start_cell] = 3 - self.__current_player
        self.__updated = False
        self.__legits = []
        self.__played.remove(action)
        if not self.__played:
            self.__firstmove = True

    def score(self):
        if len(self.__legits) == 0:
            return 1
        else:
            return -1

    def race_turns_left(self, player: Player) -> int:
        """
        Calculate the minimum number of moves needed to reach the opponent's side of the board.
        """
        size = self.__size
        player_positions = [pos for pos, occupant in self.__grid.items() if occupant == player]
        length = len(player_positions)

        race_turns = 0
        for pos in player_positions:
            distance = size - 1 - pos[0] if player == 1 else size - 1 + pos[0]
            race_turns += distance

        return race_turns // length

    def evaluate2_board(self) -> float:
        """Evaluate the board state for the current player."""
        if len(self.__legits) == 0:
            return 5000
        else:
            player = self.__current_player
            opponent = 3 - player
            center = 0

            positions_importantes = [(0, 0), (-1, 0), (0, -1), (1, 0), (0, 1), (1, 1), (-1, -1),
                                     (-1, 1), (1, -1), (-2, 1), (1, -2), (2, -1), (-1, 2)]

            for cell, occupant in self.__grid.items():
                if occupant == player:
                    if cell in positions_importantes:
                        center += 1
                elif occupant == opponent:
                    if cell in positions_importantes:
                        center -= 1

            player_legits = len(self.get_legits())
            self.set_player(opponent)
            opponent_legits = len(self.get_legits())
            self.set_player(player)
            diff_legits = opponent_legits - player_legits
            race_turn = self.race_turns_left(opponent) - self.race_turns_left(player)

            evaluation = (
                    5 * center +
                    5 * diff_legits +
                    3 * race_turn
            )

            return -evaluation

    def final(self) -> bool:
        """returns if game has ended"""
        self.__verify_update()
        if self.__legits:
            return True
        return False

    def strategy_mc(self, nb_iter: int = 1000) -> Action:
        """Monte Carlo strategy"""
        self.__verify_update()
        if len(self.__legits) == 1:
            return self.__legits[0]

        best_value: float = -float('inf')
        best_action: Action = None

        for action in self.__legits:
            gain: float = 0.0
            victoire_rouge: int = 0
            victoire_bleu: int = 0

            for _ in range(nb_iter // (len(self.__legits) + 1)):
                stack = deque()
                stack.append(action)
                self.make_move(action)
                self.set_player(3 - self.get_player())

                while self.final():
                    tmp_action: Action = self.strategy_random()
                    if self.is_legit(tmp_action):
                        stack.append(tmp_action)
                        self.make_move(tmp_action)
                        self.set_player(3 - self.get_player())

                if self.score() == 1:
                    if self.get_player() == 1:
                        victoire_rouge += 1
                    else:
                        victoire_bleu += 1
                else:
                    if self.get_player() == 2:
                        victoire_rouge += 1
                    else:
                        victoire_bleu += 1

                while stack:
                    self.unmake_move(stack.pop())
                    self.set_player(3 - self.get_player())

            if self.get_player() == 1:
                gain = victoire_rouge / nb_iter
            else:
                gain = victoire_bleu / nb_iter

            if gain > best_value:
                best_value = gain
                best_action = action

        return best_action


    def __negamax_memoize(func):
        """Cache pour negamax"""

        def memoized_func(self, depth: int, alpha: float, beta: float, player: int):
            """wrapped func"""
            self.__verify_update()
            state = get_state_negamax(self.__grid)

            if state in self.__negamax_cache:
                cached_entry = self.__negamax_cache[state]
                if cached_entry["depth"] >= depth:
                    return cached_entry["value"]

            max_eval = func(self, depth, alpha, beta, player)

            flag = "exact"
            if max_eval <= alpha:
                flag = "upperbound"
            elif max_eval >= beta:
                flag = "lowerbound"

            if state not in self.__negamax_cache or self.__negamax_cache[state]["depth"] < depth:
                self.__negamax_cache[state] = {
                    "value": max_eval,
                    "depth": depth,
                    "flag": flag
                }
            return max_eval

        return memoized_func

    def __negamax_depth(self) -> int:
        """depth for negamax"""
        if self.__size <= 3: return 12
        depths: dict[int, int] = {4: 5, 5: 10, 6: 8, 7: 7, 8: 6, 9: 6, 10: 5}
        return depths.get(self.__size, 4)

    @__negamax_memoize
    def __negamax(self, depth: int, alpha: float, beta: float, player: int) -> float:
        """Négamax avec élagage alpha-beta et mise en cache"""
        self.__verify_update()

        if depth == 0 or not self.__legits:
            return self.__evaluate_negamax(player)

        max_eval = float("-inf")

        for move in self.__legits:
            self.make_move(move)
            self.set_player(3 - self.__current_player)
            eval_value = -self.__negamax(depth - 1, -beta, -alpha, 3 - player)
            self.unmake_move(move)
            self.set_player(player)
            max_eval = max(max_eval, eval_value)
            alpha = max(alpha, eval_value)
            if alpha >= beta:
                break

        return max_eval

    def __negamax_action(self, depth: int = 3) -> tuple[float, Action]:
        """returns negamax action with alpha-beta pruning"""
        best_move: tuple[Cell, Cell]
        max_eval = float("-inf")
        alpha = float("-inf")
        beta = float("inf")

        player = self.__current_player

        for move in self.__legits:
            self.make_move(move)
            self.set_player(3 - player)
            eval_value = -self.__negamax(depth - 1, -beta, -alpha, 3 - player)
            self.unmake_move(move)
            self.set_player(player)
            if eval_value > max_eval:
                max_eval = eval_value
                best_move = move

        return max_eval, best_move

    def __evaluate_negamax(self, player: int) -> float:
        """evaluate func for negamax"""
        return self.evaluate2_board() if self.__current_player == player else -self.evaluate2_board()

    def strategy_negamax(self) -> Action:
        """Stratégie de jeu utilisant Négamax"""
        depth: int = self.__negamax_depth()
        tmp: list[Cell] = self.__played.copy()
        value = self.__negamax_action(depth)[1]
        self.__played = tmp
        return value

    def strategy_mcts(self) -> Action:
        """Stratégie de jeu utilisant MCTS"""
        return mcts(self.copy())

    def strategy_random(self) -> Action:
        """function to play with a random strat"""
        self.__verify_update()
        if len(self.__legits) == 0:
            raise ValueError("Attention plus d'action possibles")
        value = random.randint(0, len(self.__legits) - 1)
        return self.__legits[value]

    def get_player(self) -> Player:
        """getter pour l'attribut joueur actuel"""
        return self.__current_player

    def set_player(self, player: Player):
        """setter pour le joueur actuel"""
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

    def save_state(self) -> dict:
        """sauvegarde l'état du jeu"""
        # utilisée dans MCTS
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
            "negamax_cache": self.__negamax_cache,
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
        self.__negamax_cache = state["negamax_cache"]

    def to_environnement(self) -> dict:
        """sauvegarde de l'environnement"""
        return {
            "grid": self.__grid.copy(),
            "current_player": self.__current_player,
            "firstmove": self.__firstmove,
            "size": self.__size,
            "legits": self.__legits,
            "played": self.__played,
            "starting": self.__starting,
            "updated": False,
            "game": "dodo",
            "first_visit": self.__first_visit,
            "negamax_cache": self.__negamax_cache,
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
                        self.__grid.get(key) == 0 and item == opponent
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




