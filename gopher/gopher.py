"""définition des fonctions de la classe du jeu gopher"""

import time
import copy
from utils import *
from mcts import *


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
        new_game = copy.deepcopy(self)
        new_game.grid = self.__grid.copy()
        new_game.set_player(self.__current_player)
        new_game.firstmove = self.__firstmove
        new_game.size = self.__size
        return new_game

    def get_neighbors(self, x: int, y: int) -> list[Cell]:
        """gets neighbors of a cell from no data"""
        """High time complexity care  ! """
        max: int = math.floor((self.__size * 2 - 1) / 2)
        if x > max or x < -max or y > max or y < -max:
            raise ValueError("Case non dans le tableau")
        neighbors: list[Cell] = []
        closes: tuple[int, int, int] = (-1, 0, 1)
        for value_x in closes:
            for value_y in closes:
                vx: int = x + value_x
                vy: int = y + value_y
                if (
                    -max <= vx <= max
                    and -max <= vy <= max
                    and (vx, vy) != (x, y)
                    and (value_x, value_y) != (1, -1)
                    and (value_x, value_y) != (-1, 1)
                ):
                    key: Cell = (vx, vy)
                    if key in self.__grid.keys():
                        stored_value = self.__grid[key]
                        if stored_value != -1 and key not in neighbors:
                            neighbors.append(key)
        return neighbors

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

    def score_j1(self) -> float:
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
        """minmax function"""
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
                if score > best_value:
                    best_value = score
                    best = (score, move)
                self.__grid = original_grid.copy()  # Restaurer la grille initiale
                self.set_player(1)
            return best

        if self.__current_player == 2:
            best_value = float("inf")
            for move in self.__legits:
                self.move(move)
                self.set_player(1)
                score, _ = self.minmax_action(depth - 1)
                if score < best_value:
                    best_value = score
                    best = (score, move)
                self.__grid = original_grid.copy()  # Restaurer la grille initiale
                self.set_player(2)
            return best

        raise ValueError("Joueur inconnu")

    def strategy_minmax(self) -> Action:
        """strategy de jeu avec minmax"""
        length : int = len(self.__played)
        if self.__firstmove or (0,0) in self.__legits:
            return (0, 0)
        elif length>1 and self.__starting == self.__current_player and self.__size%2==1:
            length-=1
            next_cell : Cell = self.get_direction()
            if next_cell in self.__legits:return next_cell
        value: Action = self.minmax_action(self.__profondeur)[1]
        return value

    def alpha_beta_action(
        self, depth: int = 0, alpha: float = float("-inf"), beta: float = float("inf")
    ) -> tuple[float, Action]:
        """Algorithme alpha-beta"""
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
                if score > best_value:
                    best_value = score
                    best = (score, move)
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
                if score < best_value:
                    best_value = score
                    best = (score, move)
                self.__grid = original_grid.copy()  # Restaurer la grille initiale
                self.set_player(2)
                if best_value <= alpha:
                    break  # Coupure alpha
            return best

        raise ValueError("Joueur inconnu")

    def strategy_alpha_beta(self) -> Action:
        """strategy de jeu avec minmax"""
        length : int = len(self.__played)
        if self.__firstmove or (0,0) in self.__legits:
            return (0, 0)
        elif length>1 and self.__starting == self.__current_player and self.__size%2==1:
            length-=1
            next_cell : Cell = self.get_direction()
            if next_cell in self.__legits:return next_cell
        value: Action = self.alpha_beta_action(self.__profondeur)[1]
        return value

    def strategy_mcts(self, iterations : int) -> Action:
        if self.__firstmove:
            return (0, 0)
        mcts_search = MCTS(self.copy())
        return mcts_search.search(iterations)


    def strategy_random(self) -> Action:
        """function to play with a random strat"""
        self.verif()
        value = random.randint(0, len(self.__legits) - 1)
        return self.__legits[value]

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

    def get_legits(self)-> list[Cell] :
        """getter pour l'attrbut legit"""
        self.verif();return self.__legits

    def get_direction(self) -> Cell:
        last : Cell = self.__played[-1]
        value = self.__grid[last]
        verif = 0
        aligned = None
        for tup in self.get_neighbors(last[0],last[1]):
            if self.__grid[tup] == 3-value:
                # un seul résultat 
                verif+=1
                aligned = tup
        if verif >1 or verif ==0:
            raise ValueError("Incohérence dans le jeu")
        dx : int = last[0] - aligned[0]
        dy : int = last[1] - aligned[1]
        next_cell = (last[0]+dx,last[1]+dy)
        return next_cell




# CONCLUSIONS DES TESTS A CE JOUR :

# si on commence sur une taille impair l'IA gagne à 100%
# Dans tous les autres cas alors l'IA minmax avec cache est similaire au alpha-beta m
# Je dirai à vue d'oeil que ab est meilleur que min max 
# Dans tous les autres cas si pair et/ou joueur 2 commence on gagne dans 65-90% des cas 
# face à un random


def test(iter: int, size: int, depth: int,starting : Player,mcts_iter : int) -> None:
    score: int = 0
    tps1 = time.time()
    for i in range(iter):
        if iter > 1:
            clear()
            print(f"Avancement : ", end=" ")
            compteur: int = math.ceil((i / iter) * 100)
            print("[" + compteur * "-" + ((100 - compteur) * " " + "]"))
        game = Gopher_Game(size=size, starting_player=starting)
        game.set_depth(depth)
        while game.final():
            if game.get_player() == 1:
                play: Action = game.strategy_random()
                game.move(play)
                game.set_player(player=2)
            else:
                play: Action = game.strategy_mcts(mcts_iter)
                game.move(play)
                game.set_player(player=1)
        # on compte le nombre de parties gagnées par le joueur 1
        if game.get_player() == 1:
            if game.score() == 1:
                score += 1
        else:
            if game.score() == -1:
                score += 1
        print(game)
        del game

    temps: float = time.time() - tps1
    print()
    print(
        f"Nombre d'itérations : {iter} | Taille de la grille : {size} | pronfondeur : {depth} | joueur de départ : {starting}"
    )
    print(f"Temps d'éxécution  : {temps:.4f} secondes")
    if iter > 1:
        print(f"Temps par partie  : {temps/iter:.4f} secondes")
    print(
        f"Nombre de parties gagnées pour le joueur 1: {score} {(score/iter)*100:.2f}%"
    )
    print(
        f"Nombre de parties gagnées pour le joueur 2: {iter-score} {((iter-score)/iter)*100:.2f}%"
    )


def debug() -> None:

    # bug dans la vérification des coups legits
    game = Gopher_Game(3, 1)
    game.move((0,0))
    game.set_player(2)
    game.move((-1,0))
    game.set_player(1)
    game.get_direction()

    # symétries
    """
    game.grid = invert_grid_h(game.grid)
    print(game)
    game.grid = invert_grid_v(game.grid)
    print(game)
    game.grid = invert_grid_h(game.grid)
    print(game)
    game.grid = invert_grid_v(game.grid)
    print(game)
    """
    # rotations
    # rotate_grid(game.grid)

#debug()
test(iter=10000, size=4, depth=2,starting=1, mcts_iter=100)
