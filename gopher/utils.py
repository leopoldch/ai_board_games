from typing import Union,Optional
import os
import math
import random

Environment = dict
Cell = tuple[int, int]
ActionGopher = Cell
ActionDodo = tuple[Cell, Cell]
Action = Union[ActionGopher, ActionDodo]
Player = int
State = list[tuple[Cell, Player]]
Score = int
Time = int
Grid = dict[Cell:Player]


# Utilitary functions : 

def clear():
    """Efface la console"""
    if os.name == 'nt':  # Pour Windows
        os.system('cls')
    else:  # Pour Unix/Linux/MacOS
        os.system('clear')

def str_red(text: str) -> str:
    """print text in red"""
    return "\033[31m" + text + "\033[0m"

def str_blue(text: str) -> str:
    """print text in blue"""
    return "\033[34m" + text + "\033[0m"

def state_to_grid(state: State) -> Grid:
    """convert grid to state"""
    grid: Grid = {}
    for item in state:
        grid[item[0]] = item[1]
    return grid

def grid_to_state(grid: Grid) -> State:
    """convert state to grid"""
    state: State = []
    for item, key in grid.items():
        state.append((item, key))
    return state

def memoize(func):
    cache = {}
    def memoized_func(self, depth=3):
        key = tuple((pos, val) for pos, val in self.grid.items())
        if key in cache and self.is_legit(cache[key][1]):
            return cache[key]
        result = func(self, depth)
        tup : Cell = result[1]
        eval : int = result[0]
        if tup!= None:
            cache[key] = result
            # symétries horizontales et verticales
            t1 : Grid = self.grid
            s1 = invert_grid_h(t1)
            r1 = invert_coord_h(tup)
            r1 = (eval,r1)
            key = tuple((pos, val) for pos, val in s1.items())
            cache[key] = r1

            s2 = invert_grid_v(s1)
            r2 = invert_coord_v(r1[1])
            r2 = (eval,r2)
            key = tuple((pos, val) for pos, val in s2.items())
            cache[key] = r2

            s3 = invert_grid_h(s2)
            r3 = invert_coord_h(r2[1])
            r3 = (eval,r3)
            key = tuple((pos, val) for pos, val in s3.items())
            cache[key] = r3

            s4 = invert_grid_v(s3)
            r4 = invert_coord_v(r3[1])
            r4 = (eval,r4)
            key = tuple((pos, val) for pos, val in s4.items())
            cache[key] = r4

            s1 = invert_grid_v(t1)
            r1 = invert_coord_v(tup)
            r1 = (eval,r1)
            key = tuple((pos, val) for pos, val in s1.items())
            cache[key] = r1

            s2 = invert_grid_h(s1)
            r2 = invert_coord_h(r1[1])
            r2 = (eval,r2)
            key = tuple((pos, val) for pos, val in s2.items())
            cache[key] = r2

            s3 = invert_grid_v(s2)
            r3 = invert_coord_v(r2[1])
            r3 = (eval,r3)
            key = tuple((pos, val) for pos, val in s3.items())
            cache[key] = r3

            s4 = invert_grid_h(s3)
            r4 = invert_coord_h(r3[1])
            r4 = (eval,r4)
            key = tuple((pos, val) for pos, val in s4.items())
            cache[key] = r4

        return result
    return memoized_func

def invert_coord_h(cell : Cell) -> Cell:
    return (-cell[0],-cell[1])

def invert_coord_v(cell : Cell) -> Cell:
    return (cell[1],cell[0])

def invert_grid_h(grid : Grid) -> Grid:
    """invert grid horizontally"""
    new_grid : Grid = {}
    for tup in grid:
        new_grid[invert_coord_h(tup)] = grid[tup]
    return new_grid

def invert_grid_v(grid : Grid) -> Grid:
    """invert grid horizontally"""
    new_grid : Grid = {}
    for tup in grid:
        new_grid[invert_coord_v(tup)] = grid[tup]
    return new_grid

def rang(x,y) -> int:
    value : int = 0
    if (x<=0 and y>=0) or (y<=0 and x>=0):
        value = abs(x)+abs(y)
    elif x<0 and y<0:
        value = max(-x,-y)
    else:
        value = max(x,y)
    value = abs(value)
    return value

def rotate_grid(grid :Grid) -> None:
    for tup in grid:
        x : int = tup[0]
        y : int = tup[1]
        value :int = rang(x,y)
        print(value)
        
import math
import random

class Node:
    """Classe d'un noeud de l'arbre MCTS"""

    def __init__(self, game, parent=None):
        """Initialisation des attributs"""
        self.game = game
        self.parent = parent
        self.children = []
        self.visits = 0
        self.score = 0

    def select_child(self):
        """Sélectionner le meilleur enfant du noeud actuel"""
        best_score = float('-inf')
        best_child = None
        for child in self.children:
            score = child.score / child.visits + math.sqrt(2 * math.log(self.visits) / child.visits)
            if score > best_score:
                best_score = score
                best_child = child
        return best_child

    def expand(self):
        """Jouer un nouveau coup et créer un noeud"""
        legit_moves = self.game.get_legits()
        if legit_moves:
            move = random.choice(legit_moves)
            new_game = self.game.copy()
            new_game.move(move)
            new_node = Node(new_game, self)
            self.children.append(new_node)
            return new_node
        return None

    def backpropagate(self, score):
        """Backpropagation"""
        self.visits += 1
        self.score += score
        if self.parent:
            self.parent.backpropagate(-score)

def mcts(game, iterations):
    root = Node(game.copy())
    for _ in range(iterations):
        node = root
        while True:
            if node.children:
                node = node.select_child()
            else:
                if node.game.final():
                    break
                expanded_node = node.expand()
                if expanded_node is None:
                    break
                node = expanded_node
                break
        if not node.game.final():
            node.backpropagate(node.game.score())
        else:
            move = node.game.strategy_random()  
            node.game.move(move)
            if node.game.get_player() ==1:node.game.set_player(2)
            else:node.game.set_player(1)
            node.backpropagate(node.game.score())
    if root.children:
        best_child = max(root.children, key=lambda node: node.visits)
        return best_child.game.last_move() 
    else:
        # Si root.children est vide, jouer un coup aléatoire
        print('raté')
        legit_moves = game.get_legits()
        if legit_moves:
            return random.choice(legit_moves)
        else:
            return None



