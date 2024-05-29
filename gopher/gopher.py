"""définition des fonctions de la classe du jeu gopher"""
import math
import random
import time
import copy
from utils import *

class Gopher_Game:
    """classe du jeu gopher"""

    # Pour améliorer encore le temps d'éxécution il est possible de stocker 
    # les coups légaux avec un attribut de la classe qu'on met à jour à chaque 
    # changement de la grille
    # idée : parcourir toute la grille et dès qu'une valeur est différente alors
    # on regarde parmis ses voisins si d'autres coups sont légaux 
    # de cette manière c'est moins couteux que de reparcourir toute la grille
    # à chaque fois qu'on veut connaitre les coups légaux
    # fonction check_grid() qu'on peut appeller à des moments clés 


    def __init__(self,size:int, starting_player : Player) -> None:
        self.size = size
        self.profondeur = 3
        self.firstmove = True
        self.current_player = starting_player
        self.grid : Grid
        self.create_board()
    
    def set_player(self,player:Player):
        if player not in [1,2]:raise ValueError("Le joueur doit être soit 1 soit 2")
        self.current_player = player

    def create_board(self) -> None:
        """create board using a size"""
        sizet = self.size * 2 - 1
        
        self.grid: dict[Cell:Player] = {}
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
                    self.grid[cell] = 0
                counter += 1
                start = [start[0] - 1, start[1] - 1]
            else:
                for i in range(counter):
                    cell: Cell = (start[0] + i, start[1])
                    self.grid[cell] = 0
                counter -= 1
                start = [start[0], start[1] - 1]
        
    def __str__(self) -> str:
        """prints the board"""
        sizet: int = self.size * 2 - 1
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
                    case: int = self.grid[cell]
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
                    case: int = self.grid[cell]
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
            new_game.grid = self.grid.copy()
            new_game.set_player(self.current_player) 
            new_game.firstmove = self.firstmove
            new_game.size = self.size
            return new_game

    def get_neighbors(self,x: int, y: int) -> list[Cell]:
        """gets neighbors of a cell from no data"""
        """High time complexity care  ! """
        max: int = math.floor((self.size * 2 - 1)/2)
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
                    if key in self.grid.keys():
                        stored_value = self.grid[key]
                        if stored_value != -1 and key not in neighbors:
                            neighbors.append(key)
        return neighbors

    def is_legit(self, start: Cell) -> bool:
        """returns if move is legit or not"""  
        if self.firstmove:return True
        if start == None:return False
        if self.grid[start] != 0:return False
        neighbors: list[Cell] = self.get_neighbors(start[0], start[1])
        verif: int = 0
        for item in neighbors:
            if self.grid[(item[0], item[1])] == self.current_player:
                return False
            if self.current_player == 1:
                if self.grid[(item[0], item[1])] == 2:
                    verif += 1
            elif self.current_player == 2:
                if self.grid[(item[0], item[1])] == 1:
                    verif += 1
        if verif == 1:
            return True
        return False

    def legit_moves(self) -> list[Cell]:
        """returns legit moves in game"""
        results: list[Cell] = []
        if self.firstmove:return list(self.grid.keys())
        for item in self.grid.items():
            if item[1] == 0 and self.is_legit(item[0]):
                results.append(item[0])
        return results

    def move(self, cell: Cell) -> None:
        """play item on grid"""
        if not self.is_legit(cell):
            raise ValueError("Impossible de bouger ce pion à cet endroit")
        else:
            if self.firstmove:self.firstmove = False
            self.grid[cell] = self.current_player
    
    def score(self) -> float:
        """evaluation func"""
        if self.firstmove:
            return 1
        if self.legit_moves():
            return 1
        else:
            return -1
        
    def score_j1(self) -> float:
        """evaluation func"""
        v : bool = False
        if self.current_player ==2:self.set_player(1);v=True
        if self.firstmove:
            if v:self.set_player(1)
            return 1
        if self.legit_moves():
            if v:self.set_player(1)
            return 1
        else:
            if v:self.set_player(1)
            return -1

    def final(self) -> bool:
        """returns if game has ended"""
        if self.legit_moves():
            return True
        return False
    
    #@memoize
    def minmax_action(self, depth: int = 0) -> tuple[float, Action]:
        """minmax function"""
        best: tuple[float, Action] = (None, None)
        if depth == 0 or not self.legit_moves():
            return (self.score_j1(), None)
        original_grid = self.grid.copy()  # Faire une copie de la grille initiale

        if self.current_player == 1:
            best_value = float("-inf")
            for move in self.legit_moves():
                self.move(move)
                self.set_player(2)
                score, _ = self.minmax_action(depth - 1)
                if score > best_value:
                    best_value = score
                    best = (score, move)
                self.grid = original_grid.copy()  # Restaurer la grille initiale
                self.set_player(1)
            return best

        if self.current_player == 2:
            best_value = float("inf")
            for move in self.legit_moves():
                self.move(move)
                self.set_player(1)
                score, _ = self.minmax_action(depth - 1)
                if score < best_value:
                    best_value = score
                    best = (score, move)
                self.grid = original_grid.copy()  # Restaurer la grille initiale
                self.set_player(2)
            return best

        raise ValueError("Joueur inconnu")

    def strategy_minmax(self) -> Action:
        """strategy de jeu avec minmax"""
        if self.firstmove:return (0,0)
        value : Action = self.minmax_action(self.profondeur)[1]
        return value

    #@memoizeab
    def alpha_beta_action(self, depth: int = 0, alpha: float = float("-inf"), beta: float = float("inf")) -> tuple[float, Action]:
        """Algorithme alpha-beta"""
        best: tuple[float, Action] = (None, None)
        if depth == 0 or not self.legit_moves():
            return (self.score_j1(), None)

        original_grid = self.grid.copy()  # Faire une copie de la grille initiale

        if self.current_player == 1:
            best_value = float("-inf")
            for move in self.legit_moves():
                self.move(move)
                self.set_player(2)
                score, _ = self.alpha_beta_action(depth - 1, best_value, beta)
                if score > best_value:
                    best_value = score
                    best = (score, move)
                self.grid = original_grid.copy()  # Restaurer la grille initiale
                self.set_player(1)
                if best_value >= beta:
                    break  # Coupure bêta
            return best

        if self.current_player == 2:
            best_value = float("inf")
            for move in self.legit_moves():
                self.move(move)
                self.set_player(1)
                score, _ = self.alpha_beta_action(depth - 1, alpha, best_value)
                if score < best_value:
                    best_value = score
                    best = (score, move)
                self.grid = original_grid.copy()  # Restaurer la grille initiale
                self.set_player(2)
                if best_value <= alpha:
                    break  # Coupure alpha
            return best

        raise ValueError("Joueur inconnu")

    def strategy_alpha_beta(self) -> Action:
        """strategy de jeu avec minmax"""
        if self.firstmove:return (0,0)
        value : Action = self.alpha_beta_action(self.profondeur)[1]
        return value

    def strategy_random(self) -> Action:
        """function to play with a random strat"""
        legits: list[Cell] = self.legit_moves()
        value = random.randint(0,len(legits)-1)
        return legits[value]

    def update_grid_from_state(self, state : State) -> None:
        self.grid = state_to_grid(state)

    def get_state_from_grid(self) -> State:
        return grid_to_state(self.grid)


def test(iter:int,size:int, depth : int) ->None:
    score : int =0
    tps1 = time.time()
    for i in range(iter):
        clear()
        if iter >1:
            print(f'Avancement : ',end=" ")
            compteur : int = math.ceil((i/iter)*100)
            print('['+compteur*'-'+((100-compteur)*' '+']'))
        game = Gopher_Game(size=size,starting_player=1)
        game.profondeur = depth
        while game.final():
            if game.current_player==1:
                play : Action = game.strategy_minmax()
                game.move(play)
                game.set_player(player=2)
            else:
                play : Action = game.strategy_random()
                game.move(play)
                game.set_player(player=1)
        # on compte le nombre de parties gagnées par le joueur 1
        if game.current_player == 1:
            if game.score() == 1:score+=1
            #else:print(game);print(game.grid)
        else:
            if game.score() == -1:score+=1
            #else:print(game);print(game.grid)
        print(game)
        del game

    temps : float = time.time() - tps1
    print()
    print(
            f"Nombre d'itérations : {iter} | Taille de la grille : {size} | pronfondeur minmax : {depth}"
        )
    print(
        f"Temps d'éxécution  : {temps:.4f} secondes"
    )
    print(
        f"Temps par partie  : {temps/100:.4f} secondes"
    )
    print(
        f"Nombre de parties gagnées pour le joueur 1: {score} {(score/iter)*100:.2f}%"
    )
    print(
        f"Nombre de parties gagnées pour le joueur 2: {iter-score} {((iter-score)/iter)*100:.2f}%"
    )
    

def debug() -> None:

    game = Gopher_Game(7,1)

    test = {(0, 6): 0, (1, 6): 0, (2, 6): 1, (3, 6): 0, (4, 6): 2, (5, 6): 0, (6, 6): 1, (-1, 5): 2, (0, 5): 1, (1, 5): 0, (2, 5): 2, (3, 5): 0, (4, 5): 1, (5, 5): 0, (6, 5): 2, (-2, 4): 1, (-1, 4): 0, (0, 4): 2, (1, 4): 0, (2, 4): 1, (3, 4): 0, (4, 4): 2, (5, 4): 1, (6, 4): 0, (-3, 3): 0, (-2, 3): 2, (-1, 3): 0, (0, 3): 1, (1, 3): 0, (2, 3): 2, (3, 3): 1, (4, 3): 0, (5, 3): 0, (6, 3): 1, (-4, 2): 0, (-3, 2): 1, (-2, 2): 0, (-1, 2): 0, (0, 2): 2, (1, 2): 1, (2, 2): 0, (3, 2): 2, (4, 2): 1, (5, 2): 2, (6, 2): 0, (-5, 1): 1, (-4, 1): 0, (-3, 1): 2, (-2, 1): 1, (-1, 1): 0, (0, 1): 0, (1, 1): 2, (2, 1): 0, (3, 1): 0, (4, 1): 0, (5, 1): 1, (6, 1): 2, (-6, 0): 0, (-5, 0): 2, (-4, 0): 1, (-3, 0): 0, (-2, 0): 0, (-1, 0): 2, (0, 0): 1, (1, 0): 0, (2, 0): 0, (3, 0): 1, (4, 0): 2, (5, 0): 0, (6, 0): 1, (-6, -1): 1, (-5, -1): 0, (-4, -1): 2, (-3, -1): 1, (-2, -1): 0, (-1, -1): 0, (0, -1): 2, (1, -1): 0, (2, -1): 2, (3, -1): 0, (4, -1): 0, (5, -1): 2, (-6, -2): 2, (-5, -2): 0, (-4, -2): 0, (-3, -2): 2, (-2, -2): 0, (-1, -2): 1, (0, -2): 0, (1, -2): 1, (2, -2): 0, (3, -2): 0, (4, -2): 1, (-6, -3): 1, (-5, -3): 0, (-4, -3): 1, (-3, -3): 0, (-2, -3): 0, (-1, -3): 2, (0, -3): 0, (1, -3): 0, (2, -3): 1, (3, -3): 2, (-6, -4): 2, (-5, -4): 0, (-4, -4): 2, (-3, -4): 1, (-2, -4): 0, (-1, -4): 1, (0, -4): 0, (1, -4): 2, (2, -4): 0, (-6, -5): 1, (-5, -5): 0, (-4, -5): 0, (-3, -5): 2, (-2, -5): 0, (-1, -5): 2, (0, -5): 0, (1, -5): 1, (-6, -6): 2, (-5, -6): 1, (-4, -6): 0, (-3, -6): 0, (-2, -6): 0, (-1, -6): 0, (0, -6): 2}
    game.grid = test
    game.firstmove = False

    # symétries 
    '''
    game.grid = invert_grid_h(game.grid)
    print(game)
    game.grid = invert_grid_v(game.grid)
    print(game)
    game.grid = invert_grid_h(game.grid)
    print(game)
    game.grid = invert_grid_v(game.grid)
    print(game)
    '''

    # rotations

    rotate_grid(game.grid)

#debug()

test(100,3,10000)