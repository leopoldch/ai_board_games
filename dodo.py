"""file to define the structure of the board and its behavior"""
import math
import random
import time
from typing import Union

Environment = dict
Cell = tuple[int, int]
ActionGopher = Cell
ActionDodo = tuple[Cell, Cell] # case de départ -> case d'arrivée
Action = Union[ActionGopher, ActionDodo]
Player = int # 1 ou 2
State = list[tuple[Cell, Player]] # État du jeu pour la boucle de jeu
Score = int
Time = int
Grid = dict[Cell:Player]

# utilitary fonctions to make the code more readable

def str_red(text: str) -> str:
    """Colors text, red"""
    return "\033[31m" + text + "\033[0m"

def str_blue(text: str) -> str:
    """Colors text, red"""
    return "\033[34m" + text + "\033[0m"

def state_to_grid(state:State) -> Grid:
    grid : Grid ={} # stocke l'état de la grille
    for item in state:
        grid[item[0]]=item[1]
    return grid

def grid_to_state(grid:Grid) -> State:
    state : State = []
    for item, key in grid.items():
            state.append((item,key))
    return state

# ======================= grid template =======================
# documentation https://www.redblobgames.com/grids/hexagons/#map-storage

def size(state:State) -> int:
    """get size of grid"""
    grid : Grid = state_to_grid(state)
    size1 : int = 0
    size2 : int = -1
    verif1 : bool = True
    verif2 : bool = True
    while verif1:
        try:
            _=grid[(0,size1)]
            size1+=1
        except:
            verif1 = False
    while verif2:
        try:
            _=grid[(0,size2)]
            size2-=1
        except:
            verif2 = False
    return size1+abs(size2)-1

def create_board(size: int) -> State:
        """initialize the grid"""

        size = size*2 -1

        if size < 6:
            raise ValueError("La grille ne peut pas être inférieure à 6")
        grid : dict[Cell:Player] ={} # stocke l'état de la grille
        size = size # dimensions de la grille
        firstmove = True

        # variables pour initialiser l'hexagone
        counter: int = math.ceil(size / 2)
        start = [0, math.floor(size/2)]
        verif: bool = True
        iterations: int = size

        if size % 2 == 0:
            iterations += 1
        for _ in range(iterations):
            if counter == size:
                verif = False
            if verif:
                for i in range(counter):
                    cell : Cell = (start[0]+i,start[1])
                    grid[cell] = 0
                counter += 1
                start = [start[0]-1,start[1]-1]
            else:
                for i in range(counter):
                    cell : Cell = (start[0]+i,start[1])
                    grid[cell] = 0
                counter -= 1
                start = [start[0],start[1]-1]

        return grid_to_state(grid)

def init_board(board: State) -> State:
    """Checkers placement"""
    taille = (size(board) + 1) // 2
    grid: Grid = state_to_grid(board)
    top = (0, taille - 1)
    bot = (-(taille - 1), 0)

    for i in range(taille):
        top_pos = (top[0], top[1])
        bot_pos = (bot[0], bot[1])

        for _ in range(taille - i):
            grid[top_pos] = 2
            grid[bot_pos] = 1
            top_pos = (top_pos[0] + 1, top_pos[1] - 1)
            bot_pos = (bot_pos[0] + 1, bot_pos[1] - 1)

        top = (top[0] + 1, top[1])
        bot = (bot[0], bot[1] - 1)
    line_bot = (-(taille - 2), 0)
    line_top = (0, taille - 2)
    for i in range(taille - 1):
        grid[line_top] = 2
        grid[line_bot] = 1
        line_top = (line_top[0] + 1, line_top[1] - 1)
        line_bot = (line_bot[0] + 1, line_bot[1] - 1)

    return grid_to_state(grid)







def print_board(state:State) -> None:
    """print function"""

    grid : Grid = state_to_grid(state)
    sizet : int = size(state)
    print(sizet)

    returned_str: str = ""
    # variables pour initialiser l'hexagone
    counter: int = math.ceil(sizet / 2)
    start = [0, math.floor(sizet/2)]
    verif: bool = True
    iterations: int = sizet

    if sizet % 2 == 0:
        iterations += 1
    for _ in range(iterations):

        if counter == sizet:
            verif = False

        if verif:
            returned_str += " "*(sizet-counter)
            for i in range(counter):
                cell : Cell = (start[0]+i,start[1])
                case : int = grid[cell]
                if case == 1:
                    tmp : str = str_red("*")
                    returned_str += f"{tmp} "
                elif case == 2:
                    tmp : str = str_blue("*")
                    returned_str += f"{tmp} "
                else:
                    returned_str += "* "
            returned_str +="\n"
            counter += 1
            start = [start[0]-1,start[1]-1]
        else:
            returned_str += " "*(sizet-counter)
            for i in range(counter):
                cell : Cell = (start[0]+i,start[1])
                case : int = grid[cell]
                if case == 1:
                    tmp : str = str_red("*")
                    returned_str += f"{tmp} "
                elif case == 2:
                    tmp : str = str_blue("*")
                    returned_str += f"{tmp} "
                else:
                    returned_str += "* "
            returned_str +="\n"
            counter -= 1
            start = [start[0],start[1]-1]
    print(returned_str)


def is_legit(state: State, action: ActionDodo, player: Player) -> bool:
        """returns if move is legit or not"""

        grid = state_to_grid(state)

        # si la case n'est pas occupé par le joueur qui veut deplacer ce pion on retourne faux
        if grid[action[0]] != player:
            return False
        # si la case future est occupée alors on retourne faux
        if grid[action[1]] != 0:
            return False
        #deplacements possibles a partir d'une case
        if player == 1:
            directions = [(1, 0), (1, 1), (0, 1)]
        elif player == 2:
            directions = [(-1, 0), (-1, -1), (0, -1)]

        #liste des cases possibles après un deplacement possible
        cellules_possibles = [(action[0][0] + direction[0], action[0][1] + direction[1]) for direction in directions]
        if action[1] in grid and action[1] in cellules_possibles:
            return True
        return False




def legit_moves(state: State, player: Player) -> list[ActionDodo]:
    """ return list of legit moves for a player and a current state of the game """

    legit_move: list[ActionDodo] = []
    grid: Grid = state_to_grid(state)
    if player == 1:
        directions = [(1, 0), (1, 1), (0, 1)]  # possibilité de deplacement
    elif player == 2:
        directions = [(-1, 0), (-1, -1), (0, -1)]

    for cellule, occupant in grid.items():
        if occupant == player: # si la case n'est pas occupé par le joueur qui veut deplacer ce pion on n'ajoute pas
            for direction in directions:
                nouvelle_cellule = (cellule[0] + direction[0], cellule[1] + direction[1])
                if nouvelle_cellule in grid and grid[nouvelle_cellule] == 0: # si la case future n'existe pas ou/et est occupée alors on n'ajoute pas
                    legit_move.append((cellule, nouvelle_cellule))

    return legit_move


def move(state:State, action : ActionDodo, player : Player) -> State:
    """ function to allow users to place new items on boards following rules """

    if not is_legit(state, action, player):
        raise ValueError("Impossible de bouger ce pion à cet endroit")
    else:
        grid: Grid = state_to_grid(state)
        start_cell, end_cell = action
        grid[end_cell] = player # on place le pion dans la position d'arrivée
        grid[start_cell] = 0  # on enleve le pion de la position de départ

    return grid_to_state(grid)

def is_game_over(state: State, player: Player) -> bool:
    """Checks if the game is over. """

    return len(legit_moves(state, player)) == 0

def score(state: State, player: Player) -> float:
    """   return a score based on who won at the end. """



    other_player = 3 - player # permet d'avoir l'autre joueur
    if is_game_over(state, player):
        return 1  # le joueur actuelle a gané

    elif is_game_over(state, other_player):
        return - 1 # l autre joueur a gagné
    else:
        return 0  # pas terminé


def final(state: State) -> bool:
    """Check if it's a final state"""
    return is_game_over(state,1) or is_game_over(state,2)



'''
def minmax(state: State, player: Player) -> float:
    """basic min max"""
    player1: Player = 1
    player2: Player = 2
    possibilities: list[Action]
    best: float
    
    if score(state):
        return score(grid, player1)

    if player == 1:  # maximazing player
        best = float("-inf")
        possibilities = legals(grid)
        print("joueur1", possibilities)
        for item in possibilities:
            tmp = play(grid, player, item)
            val = minmax(tmp, player2)
            if max(best, val) == val:
                best = val
        return best

    if player == 2:  # minimizing player
        best = float("inf")
        possibilities = legals(grid)
        print("joueur2", possibilities)
        for item in possibilities:
            tmp = play(grid, player, item)
            val = minmax(tmp, player1)
            if min(best, val) == val:
                best = val
        return best

    raise ValueError("erreur pas de joeur connu")
'''


def strategy(env: Environment, state: State, player: Player,time_left: Time) -> tuple[Environment, Action]:
    legits : list[ActionDodo] = legit_moves(state, player)
    if len(legits)>0:
        value = random.randint(0,len(legits)-1)
        return ({},legits[value])
    else:
        return ({},[])


def test(iter : int, size : int):
    """test function"""
    tps1 = time.time()
    stats1 = 0
    stats2 = 0
    for _ in range(iter):
        current_player = 1
        board = create_board(size)
        state = init_board(board)
        plays = strategy({}, state, current_player, 0)[1]
        print("bonjourno")
        while not final(state):
            state = move(state, plays, current_player)
            if current_player == 1:current_player=2
            else:current_player=1
            #print("le current player est", current_player)
            plays = strategy({},state,current_player,0)[1]
            #print("voici le coup qui sera joué", plays)
            #print_board(state)
        print("voici le score des rouges",score(state,1),"et voici le score des bleus", score(state,2))
        if score(state,1)==1:
            stats1+=1
        elif score(state,2)==1:
            stats2+=1

    print(f"temps d'éxécution pour {iter} itérations : {time.time() - tps1:.4f} secondes")
    print(f"Nombre de parties gagnées pour le joueur 1: {(stats1/iter)*100:.2f}%")
    print(f"Nombre de parties gagnées pour le joueur 2: {(stats2/iter)*100:.2f}%")


test(50,10)
#board7 = create_board(7)
#board7 = init_board(board7)
#print(board7)
#print_board(board7)


