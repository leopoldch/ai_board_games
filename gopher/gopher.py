"""définition des fonctions de la classe du jeu gopher"""
import math
import random
from utils import *

class Gopher_Game:
    """classe du jeu gopher"""

    def __init__(self,size:int) -> None:
        self.size = size
        self.firstmove = True
        self.grid : Grid
        self.create_board()
    
    def create_board(self) -> None:
        """create board using a size"""
        sizet = self.size * 2 - 1
        if sizet < 6:
            raise ValueError("La grille ne peut pas être inférieure à 6")
        
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

    def is_legit(self, start: Cell, player: Player) -> bool:
        """returns if move is legit or not"""  
        if self.grid[start] != 0:
            return False
        if self.firstmove:
            return True
        neighbors: list[Cell] = self.get_neighbors(start[0], start[1])
        verif: int = 0
        for item in neighbors:
            if self.grid[(item[0], item[1])] == player:
                return False
            if player == 1:
                if self.grid[(item[0], item[1])] == 2:
                    verif += 1
            elif player == 2:
                if self.grid[(item[0], item[1])] == 1:
                    verif += 1
        if verif == 1:
            return True
        return False

    def legit_moves(self, player: Player) -> list[Cell]:
        """returns legit moves in game"""
        results: list[Cell] = []
        if self.firstmove:return list(self.grid.keys())
        for item in self.grid.items():
            if item[1] == 0 and self.is_legit(item[0], player):
                results.append(item[0])
        return results

    def move(self, cell: Cell, player: Player) -> None:
        """play item on grid"""
        if not self.is_legit(cell, player):
            raise ValueError("Impossible de bouger ce pion à cet endroit")
        else:
            if self.firstmove:self.firstmove = False
            self.grid[cell] = player
    
    def score(self, player: Player) -> float:
        """evaluation func"""
        if self.firstmove:
            return 1
        if player == 1:
            if self.legit_moves(1) == []:
                return -1
            else:
                return 1
        elif player == 2:
            if self.legit_moves(2) == []:
                return -1
            else:
                return 1

    def final(self) -> bool:
        """returns if game has ended"""
        if self.score(1) == 1 and self.score(2) == 1:
            return True
            
        return False
    
    def minmax_action(self, player: Player, depth: int = 0) -> tuple[float, Action]:
        """minmax function"""
        player1: Player = 1
        player2: Player = 2
        best: tuple[float, Action] = (None, None)
        if depth == 0 or not self.final():
            return (self.score(player1), best)
        
        if player == 1:
            best = (float("-inf"), best)
            for item in self.legit_moves(player):
                tmp = self.move(item, player)
                returned_values = self.minmax_action(tmp, player2, depth - 1)
                if max(best[0], returned_values[0]) == returned_values[0]:
                    best = (returned_values[0], item)
            return best
        
        if player == 2:
            best = (float("inf"), best)
            for item in self.legit_moves(player):
                tmp = self.move(item, player)
                returned_values = self.minmax_action(tmp, player1, depth - 1)
                if min(best[0], returned_values[0]) == returned_values[0]:
                    best = (returned_values[0], item)
            return best
        raise ValueError("erreur pas de joeur connu")

    def strategy_random(self, player: Player) -> tuple[Environment, Action]:
        """function to play with a random strat"""
        legits: list[Cell] = self.legit_moves(player)
        print(legits)
        value = random.randint(0,len(legits)-1)
        return ({}, legits[value])

    def update_grid_from_state(self, state : State) -> None:
        self.grid = state_to_grid(state)

    def get_state_from_grid(self) -> State:
        return grid_to_state(self.grid)


def test():
    game = Gopher_Game(7)
    cur_player : Player = 1
    while game.final():
        play : Action = game.strategy_random(cur_player)[1]
        game.move(play,cur_player)
        if cur_player ==1:cur_player=2
        else:cur_player=1
        print(game)
        print(game.final())
    print(game.final())
        
test()