"""définition de la classe du jeu gopher"""

# Dear programmer
# When I wrote this code, only god and
# I knew how it worked.
# Now, only god know it !

# Therefore, if you are trying to optimize
# the strategies and it fails (most surely),
# please increase this counter as a
# warning for the next person

# total_hours_wasted_here = 254

import math
import random
from utils.utilitary import (
    ActionGopher,
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


class GopherGame:
    """classe du jeu gopher"""

    # --------------- DESCRIPTION FONCTIONNEMENT ---------------

    # l'accès à un attribut dans un dictionnaire python (hash table)
    # est en O(1) c'est pour ça que dans le code il y a souvent
    # self.__grid.get(key)
    # ce qui prend du temps n'est pas le fonctionnement de jeu
    # mais bien l'exploration du graphe avec Negamax
    # Pour contrer cette explosion algorithmique
    # il y a un élagage alpha beta, un cache qui enregistre les
    # grilles déjà explorées
    # Les symétries ne sont pas efficaces (trop couteux)

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
        self.__negamax_cache: dict = {}
        self.__neg_update = True

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
        if self.__played:
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
        directions = [[-1, -1], [-1, 0], [0, -1], [0, 1], [1, 0], [1, 1]]
        for direction in directions:
            vx, vy = x + direction[0], y + direction[1]
            if (-max_val <= vx <= max_val) and (-max_val <= vy <= max_val):
                key = (vx, vy)
                if key in self.__grid and self.__grid.get(key) != -1:
                    neighbors.append(key)
        return neighbors

    def is_legit(self, start: Cell) -> bool:
        """returns if move is legit or not"""
        if self.__firstmove:
            return True
        if start is None or self.__grid.get(start) != 0:
            return False
        neighbors: list[Cell] = self.__get_neighbors(start[0], start[1])
        verif: int = 0
        for item in neighbors:
            if verif > 1:
                return False
            if self.__grid.get((item[0], item[1])) == self.__current_player:
                return False
            if self.__current_player == 1:
                if self.__grid.get((item[0], item[1])) == 2:
                    verif += 1
            elif self.__current_player == 2:
                if self.__grid.get((item[0], item[1])) == 1:
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

    def __unmake_move(self, cell: Cell) -> None:
        """unplay item on grid"""
        self.__grid[cell] = 0
        self.__updated = False
        self.__legits = []
        self.__played.remove(cell)
        if not self.__played:
            self.__firstmove = True

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

    # ----------------------- ALGO NEGAMAX -----------------------

    def __negamax_depth(self) -> int:
        """depth for negamax"""
        if self.__size <= 3:
            return 100000
        if self.__size == 6 and len(self.__played) > 25:
            if self.__neg_update:
                print("updaté")
                self.__negamax_cache = {}
                self.__neg_update = False
            return 9
        depths: dict[int, int] = {4: 1000, 5: 12, 6: 7, 7: 7, 8: 6, 9: 5, 10: 4}
        return depths.get(self.__size, 3)

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

    @__negamax_memoize
    def __negamax(self, depth: int, alpha: float, beta: float, player: int) -> float:
        """Négamax avec élagage alpha-beta et mise en cache"""
        self.__verify_update()

        if depth == 0 or not self.__legits:
            return self.__evaluate_negamax(player)

        max_eval = float("-inf")

        # moves = sorted(self.__legits, key=self.__evaluate_move, reverse=True)
        # rajoute bcp de complexité

        for move in self.__legits:
            self.make_move(move)
            self.set_player(3 - self.__current_player)
            eval_value = -self.__negamax(depth - 1, -beta, -alpha, 3 - player)
            self.__unmake_move(move)
            self.set_player(player)
            max_eval = max(max_eval, eval_value)
            alpha = max(alpha, eval_value)
            if alpha >= beta:
                break

        return max_eval

    def __negamax_action(self, depth: int = 3) -> tuple[float, Cell]:
        """returns negamax action with alpha-beta pruning"""
        best_move: tuple[int, int]
        max_eval = float("-inf")
        alpha = float("-inf")
        beta = float("inf")

        player = self.__current_player
        # moves = sorted(self.__legits, key=self.__evaluate_move, reverse=True)
        # rajoute bcp de complexité

        for move in self.__legits:
            self.make_move(move)
            self.set_player(3 - self.__current_player)
            eval_value = -self.__negamax(depth - 1, -beta, -alpha, 3 - player)
            self.__unmake_move(move)
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
                return 100
            return -len(tmp)
        if not tmp:
            return -100
        return len(tmp)
        # return self.score() if self.__current_player == player else -self.score()

    # ---------------- DEFINITION DES STRATÉGIES ----------------
    # la stratégie utilisée pour jouer est negamax
    # les autres sont toutes moins efficaces

    def strategy_negamax(self) -> ActionGopher:
        """Stratégie de jeu utilisant Négamax"""
        self.__verify_update()
        if len(self.__legits) == 1:
            return self.__legits[0]
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
            # si c'est pas dans les coups légaux alors on passe sur du négamax
        depth: int = self.__negamax_depth()
        # print(f"profondeur : {depth} - taille grille : {self.__size}")
        tmp: list[Cell] = self.__played.copy()
        value = self.__negamax_action(depth)[1]
        self.__played = tmp
        # print(f"cache : {len(self.__negamax_cache)}"if self.__negamax_cache else "no cache" )
        return value

    def strategy_random(self) -> ActionGopher:
        """function to play with a random strat"""
        self.__verify_update()
        if len(self.__legits) == 0:
            raise ValueError("Attention plus d'action possibles")
        value = random.randint(0, len(self.__legits) - 1)
        return self.__legits[value]

    # ---------------- GETTER ET SETTERS PUBLICS ----------------

    def get_grid(self):
        """getter de grid"""
        return self.__grid

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

    def get_player(self) -> Player:
        """getter pour l'attribut joueur actuel"""
        return self.__current_player

    def set_player(self, player: Player):
        """setter pour le joueur actuel"""
        # utilisée dans la boucle de jeu
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

        # sur unr grille impair un simple calcul permet
        # de trouver le meilleur coup

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
        self.__neg_update = state["neg_update"]

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
            "game": "gopher",
            "first_visit": self.__first_visit,
            "negamax_cache": self.__negamax_cache,
            "neg_update": self.__neg_update,
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
