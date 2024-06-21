"""définition de la classe du jeu Dodo"""

# Dear programmer
# When I wrote this code, only god and
# I knew how it worked.
# Now, only god know it !

# Therefore, if you are trying to optimize
# the strategies and it fails (most surely),
# please increase this counter as a
# warning for the next person

# total_hours_wasted_here = 253

from collections import deque
import random
import math
from copy import deepcopy
from utils.utilitary import (
    ActionDodo,
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
        self.__played: int = 0
        self.__starting: Player = starting_player
        self.__negamax_cache: dict = {}

    def copy(self):
        """constructeur de dodo"""
        new_game = DodoGame(self.__size, self.__current_player)
        new_game.set_firstmove(self.get_firstmove())
        new_game.set_first_visit(self.get_first_visit())
        new_game.set_player(self.get_player())
        new_game.set_grid(self.get_grid().copy())
        new_game.set_updated(self.get_updated())
        new_game.set_legits(self.get_legits().copy())
        new_game.set_played(self.get_played().copy())
        new_game.set_starting(self.get_starting())
        return new_game

    def __create_board(self) -> None:
        """cree la board en fonction de la size"""
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
        """Affichage basique de la grille"""
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
        if self.__played != 0:
            self.__firstmove = False
            self.__legits = []
            self.__updated = False
        if not self.__updated:
            self.__legit_moves()

    def is_legit(self, action: tuple[Cell, Cell]) -> bool:
        """returns if move is legit or not"""
        if (
            self.__grid[action[0]] != self.__current_player
            or self.__grid[action[1]] != 0
        ):
            return False

        if self.__current_player == 1:
            directions = [(1, 0), (1, 1), (0, 1)]
        elif self.__current_player == 2:
            directions = [(-1, 0), (-1, -1), (0, -1)]

        cellules_possibles = [
            (action[0][0] + direction[0], action[0][1] + direction[1])
            for direction in directions
        ]
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
                        nouvelle_cellule = (
                            cellule[0] + direction[0],
                            cellule[1] + direction[1],
                        )
                        if (
                            nouvelle_cellule in self.__grid
                            and self.__grid[nouvelle_cellule] == 0
                        ):
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
        self.__grid[end_cell] = (
            self.__current_player
        )  # on place le pion dans la position d'arrivée
        self.__updated = False
        self.__legits = []
        self.__played += 1

    def unmake_move(self, action: tuple[Cell, Cell]) -> None:
        """unplay item on grid"""
        start_cell, end_cell = action
        self.__grid[end_cell] = 0
        self.__grid[start_cell] = 3 - self.__current_player
        self.__updated = False
        self.__legits = []
        self.__played -= 1
        if self.__played == 0:
            self.__firstmove = True

    def score(self):
        """return the score"""
        if len(self.__legits) == 0:
            return 1
        return -1

    def final(self) -> bool:
        """returns if game has ended"""
        self.__verify_update()
        if self.__legits:
            return True
        return False

    def strategy_mc(self, nb_iterations: int = 1000) -> ActionDodo:
        """Monte Carlo strategy"""
        self.__verify_update()
        if len(self.__legits) == 1:
            return self.__legits[0]

        valeur_optimale: float = -float("inf")
        action_optimale: tuple[Cell, Cell] = self.__legits[0]

        def simulate(action: tuple[Cell, Cell]) -> float:
            victoire_joueur1: int = 0
            victoire_joueur2: int = 0
            total_simulations = nb_iterations // (len(self.__legits) + 1)

            for _ in range(total_simulations):
                game_copy = deepcopy(self)
                pile: deque = deque()
                pile.append(action)
                game_copy.make_move(action)
                game_copy.set_player(3 - game_copy.get_player())

                while game_copy.final():
                    tmp_action: tuple[Cell, Cell] = game_copy.strategy_random()
                    if game_copy.is_legit(tmp_action):
                        pile.append(tmp_action)
                        game_copy.make_move(tmp_action)
                        game_copy.set_player(3 - game_copy.get_player())

                if game_copy.score() == 1:
                    if game_copy.get_player() == 1:
                        victoire_joueur1 += 1
                    else:
                        victoire_joueur2 += 1
                else:
                    if game_copy.get_player() == 2:
                        victoire_joueur1 += 1
                    else:
                        victoire_joueur2 += 1

                while pile:
                    game_copy.unmake_move(pile.pop())
                    game_copy.set_player(3 - game_copy.get_player())

            recompense = (
                victoire_joueur1 / total_simulations
                if self.get_player() == 1
                else victoire_joueur2 / total_simulations
            )
            return recompense

        for action in self.__legits:
            recompense = simulate(action)
            if recompense > valeur_optimale:
                valeur_optimale = recompense
                action_optimale = action

        return action_optimale

    @staticmethod
    def __negamax_memoize(func):
        """Cache pour negamax"""

        def memoized_func(self, depth: int, alpha: float, beta: float, player: int):
            """wrapped func"""

            state = get_state_negamax(self.get_grid())

            if state in self.get_negamax_cache():
                cached_entry = self.get_negamax_cache()[state]
                if cached_entry["depth"] >= depth:
                    if cached_entry["flag"] == "exact":
                        return cached_entry["value"]
                    if (
                        cached_entry["flag"] == "lowerbound"
                        and cached_entry["value"] > alpha
                    ):
                        alpha = cached_entry["value"]
                    if (
                        cached_entry["flag"] == "upperbound"
                        and cached_entry["value"] < beta
                    ):
                        beta = cached_entry["value"]
                    if alpha >= beta:
                        return cached_entry["value"]

            max_eval = func(self, depth, alpha, beta, player)

            flag = "exact"
            if max_eval <= alpha:
                flag = "upperbound"
            elif max_eval >= beta:
                flag = "lowerbound"

            cache = self.get_negamax_cache()
            if state not in cache or cache[state]["depth"] < depth:
                self.set_negamax_cache(state, max_eval, depth, flag)
            return max_eval

        return memoized_func

    def __negamax_depth(self) -> int:
        """depth for negamax"""
        if self.__size <= 3:
            return 12
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

    def __negamax_action(self, depth: int = 3) -> tuple[float, ActionDodo]:
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
        tmp = self.get_legits()
        if self.__current_player != player:
            if not tmp:
                return -100
            return len(tmp)
        if not tmp:
            return 100
        return -len(tmp)

    def strategy_negamax(self) -> ActionDodo:
        """negamax strat"""
        depth: int = self.__negamax_depth()
        tmp: int = self.__played
        value = self.__negamax_action(depth)[1]
        self.__played = tmp
        return value

    def strategy_random(self) -> tuple[Cell, Cell]:
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

    def get_legits(self) -> list[tuple[Cell, Cell]]:
        """getter pour l'attrbut legit"""
        self.__verify_update()
        return self.__legits

    def get_played(self) -> int:
        """retourne les coups joués"""
        return self.__played

    def get_firstmove(self) -> bool:
        """getter pour firstmove"""
        return self.__firstmove

    def get_updated(self) -> bool:
        """getter pour updated"""
        return self.__updated

    def get_first_visit(self) -> bool:
        """getter pour first_visit"""
        return self.__first_visit

    def get_grid(self):
        """getter de grid"""
        return self.__grid

    def get_starting(self):
        """getter de starting"""
        return self.__starting

    def get_negamax_cache(self):
        """get negamax cache"""
        return self.__negamax_cache

    def set_negamax_cache(self, state, value, depth, flag):
        """setter de cache"""
        self.__negamax_cache[state] = {
            "value": value,
            "depth": depth,
            "flag": flag,
        }

    def set_firstmove(self, firstmove: bool):
        """Setter pour firstmove"""
        self.__firstmove = firstmove

    def set_first_visit(self, first_visit: bool):
        """Setter pour first_visit"""
        self.__first_visit = first_visit

    def set_grid(self, grid: Grid):
        """Setter pour grid"""
        self.__grid = grid

    def set_updated(self, updated: bool):
        """Setter pour updated"""
        self.__updated = updated

    def set_legits(self, legits: list[tuple[Cell, Cell]]):
        """Setter pour legits"""
        self.__legits = legits

    def set_played(self, played: int):
        """Setter pour played"""
        self.__played = played

    def set_starting(self, starting: Player):
        """Setter pour starting"""
        self.__starting = starting

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
        """Permet de remettres des attributs utile"""
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
        self.__grid = state_to_grid(state)
        self.__played += 1

        if self.__first_visit:
            if self.__played == 1:
                self.__starting = opponent
                self.__firstmove = False
                self.__legits = []
            elif self.__played == 0:
                self.__starting = current
        self.__verify_update()
