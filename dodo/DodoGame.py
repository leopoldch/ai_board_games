"""définition de la classe du jeu gopher"""
import time
import random
import math
import random
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


class DodoGame:
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
    # Les symétries ne sont pas efficaces

    # --- FONCTIONS UTILITAIRES POUR LE FONCTIONNEMENT DU JEU ---

    def __init__(self, size: int, starting_player: Player) -> None:
        """constructeur de Gopher"""
        self.__size: int = size
        self.__firstmove: bool = True #ptet a enlever
        self.__first_visit: bool = True #ptet a enlever
        self.__current_player: Player = starting_player
        self.__grid: Grid = {}
        self.__create_board()
        self.__updated: bool = False
        self.__legits: list[tuple[Cell, Cell]] = []
        self.__played: list[tuple[Cell, Cell]] = [] #ptet a enlever
        self.__starting: Player = starting_player
        self.__negamax_cache: dict = {}

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
        print(size)
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
    """
    def __get_neighbors(self, x: int, y: int) -> list[Cell]:
        '''récupérer les voisins'''
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
    """

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



    def __unmake_move(self, action: tuple[Cell, Cell]) -> None:
        '''unplay item on grid'''
        start_cell, end_cell = action
        self.__grid[end_cell] = 0
        self.__grid[start_cell] = 3 - self.__current_player #pas sur du tout a reregarder juste après
        self.__updated = False
        self.__legits = []
        self.__played.remove(action)
        if not self.__played:
            self.__firstmove = True

    """
    def race_turn_left(self,player : Player) -> int:
        if player == 1:
            directions = [(1, 0), (1, 1), (0, 1)]
        else:
            directions = [(-1, 0), (-1, -1), (0, -1)]

        race_turns = 0
        for cell, occupant in self.__grid.items():
            if occupant == player:
                min_distance = float('inf')
                for direction in directions:
                    steps = 0
                    next_cell = cell
                    while next_cell in self.__grid and self.__grid[next_cell] == 0:
                        steps += 1
                        next_cell = (next_cell[0] + direction[0], next_cell[1] + direction[1])
                    if steps < min_distance:
                        min_distance = steps
                race_turns += min_distance
        return race_turns
        """

    def score(self):
        if len(self.__legits) == 0:
            return 1
        else:
            return -1



    def evaluate2_board(self) -> float:
        """Evaluate the board state for the current player."""
        if len(self.__legits) == 0:
            return 5000
        else:
            player = self.__current_player
            opponent = 3 - player

            player_pieces = 0
            opponent_pieces = 0
            player_mobility = 0
            opponent_mobility = 0
            center_control = 0

            center_positions = [
                (0, 0), (-1, 0), (0, -1), (1, 0), (0, 1),
                (-1, 1), (1, -1), (-2, 1), (1, -2), (2, -1), (-1, 2)
            ]

            for cell, occupant in self.__grid.items():
                if occupant == player:
                    player_pieces += 1
                    if cell in center_positions:
                        center_control += 1
                    player_mobility += sum(
                        1 for direction in [(1, 0), (1, 1), (0, 1)]
                        if (cell[0] + direction[0], cell[1] + direction[1]) in self.__grid and self.__grid[
                            (cell[0] + direction[0], cell[1] + direction[1])] == 0
                    )
                elif occupant == opponent:
                    opponent_pieces += 1
                    if cell in center_positions:
                        center_control -= 1
                    opponent_mobility += sum(
                        1 for direction in [(-1, 0), (-1, -1), (0, -1)]
                        if (cell[0] + direction[0], cell[1] + direction[1]) in self.__grid and self.__grid[
                            (cell[0] + direction[0], cell[1] + direction[1])] == 0
                    )

            piece_advantage = player_pieces - opponent_pieces
            mobility_advantage = player_mobility - opponent_mobility
            #race_turn = self.race_turn_left(opponent) - self.race_turn_left(player)

            # Weight the different components of the evaluation
            evaluation = (
                    90 * piece_advantage +  # Pieces are very important
                    10 * center_control +  # Control of the center is important
                    5 * mobility_advantage  # Mobility is somewhat important
            )
            #print(evaluation)

            return -evaluation



    def final(self) -> bool:
        """returns if game has ended"""
        self.__verify_update()
        if self.__legits:
            return True
        return False

    # ----------------------- ALGO NEGAMAX -----------------------

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
                    ''' if cached_entry["flag"] == "exact":
                        return cached_entry["value"]
                    elif cached_entry["flag"] == "lowerbound" and cached_entry["value"] > alpha:
                        alpha = cached_entry["value"]
                    elif cached_entry["flag"] == "upperbound" and cached_entry["value"] < beta:
                        beta = cached_entry["value"]
                    if alpha >= beta:
                        return cached_entry["value"]'''

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
        depths: dict[int, int] = {4: 2, 5: 10, 6: 8, 7: 7, 8: 6, 9: 6, 10: 5}
        return depths.get(self.__size, 4)

    @__negamax_memoize
    def __negamax(self, depth: int, alpha: float, beta: float, player: int) -> float:
        """Négamax avec élagage alpha-beta et mise en cache"""
        self.__verify_update()

        if depth == 0 or not self.__legits:
            return self.__evaluate_negamax(player)

        max_eval = float("-inf")

        # moves = sorted(self.__legits, key=self.__evaluate_move, reverse=True) # rajoute bcp de complexité

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

    def __negamax_action(self, depth: int = 3) -> tuple[float, Action]:
        """returns negamax action with alpha-beta pruning"""
        best_move: tuple[Cell, Cell]
        max_eval = float("-inf")
        alpha = float("-inf")
        beta = float("inf")

        player = self.__current_player
        # moves = sorted(self.__legits, key=self.__evaluate_move, reverse=True) # rajoute bcp de complexité

        for move in self.__legits:
            self.make_move(move)
            self.set_player(3 - player)
            eval_value = -self.__negamax(depth - 1, -beta, -alpha, 3 - player)
            self.__unmake_move(move)
            self.set_player(player)
            if eval_value > max_eval:
                max_eval = eval_value
                best_move = move

        return max_eval, best_move

    def __evaluate_negamax(self, player: int) -> float:
        """evaluate func for negamax"""
        return self.evaluate2_board() if self.__current_player == player else -self.evaluate2_board()

    # ---------------- DEFINITION DES STRATÉGIES ----------------
    # la stratégie utilisée pour jouer est negamax
    # les autres sont toutes moins efficaces

    def strategy_negamax(self) -> Action:
        """Stratégie de jeu utilisant Négamax"""

        # si c'est pas dans les coups légaux alors on passe sur du négamax
        depth: int = self.__negamax_depth()
        # print(f"profondeur : {depth} - taille grille : {self.__size}")
        tmp: list[Cell] = self.__played.copy()
        value = self.__negamax_action(depth)[1]
        self.__played = tmp
        # print(f"cache : {len(self.__negamax_cache)}"if self.__negamax_cache else "no cache" )
        return value

    def strategy_random(self) -> Action:
        """function to play with a random strat"""
        self.__verify_update()
        if len(self.__legits) == 0:
            raise ValueError("Attention plus d'action possibles")
        value = random.randint(0, len(self.__legits) - 1)
        return self.__legits[value]


    # ---------------- GETTER ET SETTERS PUBLICS ----------------

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


def test(iter: int, size: int):
    """test function"""
    tps1 = time.time()
    stats1 = 0
    stats2 = 0

    for _ in range(iter):
        starting_player = 1
        game = DodoGame(size, starting_player)
        print(game)

        while game.final():
            if game.get_player() == 1:
                action = game.strategy_negamax()
            else:
                action = game.strategy_random()

            game.make_move(action)
            game.set_player(3 - game.get_player())  # Changer le joueur

        print(game)
        score = game.score()
        if score == 1:
            if game.get_player() == 1: # a changer ptet
                stats1 += 1
            else:
                stats2 += 1

    print(f"Temps d'exécution pour {iter} itérations : {time.time() - tps1:.4f} secondes")
    print(f"Nombre de parties gagnées pour le joueur 1: {(stats1 / iter) * 100:.2f}%")
    print(f"Nombre de parties gagnées pour le joueur 2: {(stats2 / iter) * 100:.2f}%")



test(1000, 4)
