"""file to define the structure of the board and its behavior"""

import math
import random
import time
from typing import Union

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

def size(state: State) -> int:
    """returns size of grid"""
    grid: Grid = state_to_grid(state)
    size1: int = 0
    size2: int = -1
    verif1: bool = True
    verif2: bool = True
    while verif1:
        try:
            _ = grid[(0, size1)]
            size1 += 1
        except:
            verif1 = False
    while verif2:
        try:
            _ = grid[(0, size2)]
            size2 -= 1
        except:
            verif2 = False
    return size1 + abs(size2) - 1

def create_board(size: int) -> State:
    """create board using a size"""
    size = size * 2 - 1
    if size < 6:
        raise ValueError("La grille ne peut pas être inférieure à 6")
    grid: dict[Cell:Player] = {}
    size = size
    firstmove = True
    counter: int = math.ceil(size / 2)
    start = [0, math.floor(size / 2)]
    verif: bool = True
    iterations: int = size
    if size % 2 == 0:
        iterations += 1
    for _ in range(iterations):
        if counter == size:
            verif = False
        if verif:
            for i in range(counter):
                cell: Cell = (start[0] + i, start[1])
                grid[cell] = 0
            counter += 1
            start = [start[0] - 1, start[1] - 1]
        else:
            for i in range(counter):
                cell: Cell = (start[0] + i, start[1])
                grid[cell] = 0
            counter -= 1
            start = [start[0], start[1] - 1]
    return grid_to_state(grid)

def print_board(state: State) -> None:
    """prints the board"""
    grid: Grid = state_to_grid(state)
    sizet: int = size(state)
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
                case: int = grid[cell]
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
                case: int = grid[cell]
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
    print(returned_str)

def get_neighbors(state: State, x: int, y: int) -> list[Cell]:
    """gets neighbors of a cell"""
    grid = state_to_grid(state)
    max: int = math.floor(size(state) / 2)
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
                if key in grid.keys():
                    stored_value = grid[key]
                    if stored_value != -1 and key not in neighbors:
                        neighbors.append(key)
    return neighbors

def is_legit(state: State, start: Cell, player: Player) -> bool:
    """returns if move is legit or not"""
    grid = state_to_grid(state)
    if grid[start] != 0:
        return False
    if not 1 in grid.values() and not 2 in grid.values():
        return True
    neighbors: list[Cell] = get_neighbors(state, start[0], start[1])
    verif: int = 0
    for item in neighbors:
        if grid[(item[0], item[1])] == player:
            return False
        if player == 1:
            if grid[(item[0], item[1])] == 2:
                verif += 1
        elif player == 2:
            if grid[(item[0], item[1])] == 1:
                verif += 1
    if verif == 1:
        return True
    return False


def legit_moves(state: State, player: Player) -> list[Cell]:
    """returns legit moves in game"""
    grid: Grid = state_to_grid(state)
    results: list[Cell] = []
    for item in grid.items():
        if item[1] == 0 and is_legit(state, item[0], player):
            results.append(item[0])
    return results


def move(state: State, cell: Cell, player: Player) -> State:
    """play item on grid"""
    if not is_legit(state, cell, player):
        raise ValueError("Impossible de bouger ce pion à cet endroit")
    else:
        grid: Grid = state_to_grid(state)
        grid[cell] = player
        return grid_to_state(grid)


def score(state: State, player: Player) -> float:
    """evaluation func"""
    grid: Grid = state_to_grid(state)
    if not 1 in grid.values() and not 2 in grid.values():
        return 1
    if player == 1:
        if legit_moves(state, 1) == [] and 2 in grid.values():
            return -1
        else:
            return 1
    elif player == 2:
        if legit_moves(state, 2) == [] and 1 in grid.values():
            return -1
        else:
            return 1


def final(state) -> bool:
    """returns if game has ended"""
    if score(state, 1) == 1 and score(state, 2) == 1:
        return True
    return False


def minmax_action(grid: State, player: Player, depth: int = 0) -> tuple[float, Action]:
    """minmax function"""
    player1: Player = 1
    player2: Player = 2
    best: tuple[float, Action] = (None, None)
    if depth == 0 or not final(grid):
        return (score(grid, player1), best)
    if player == 1:
        best = (float("-inf"), best)
        for item in legit_moves(grid, player):
            tmp = move(grid, item, player)
            returned_values = minmax_action(tmp, player2, depth - 1)
            if max(best[0], returned_values[0]) == returned_values[0]:
                best = (returned_values[0], item)
        return best
    if player == 2:
        best = (float("inf"), best)
        for item in legit_moves(grid, player):
            tmp = move(grid, item, player)
            returned_values = minmax_action(tmp, player1, depth - 1)
            if min(best[0], returned_values[0]) == returned_values[0]:
                best = (returned_values[0], item)
        return best
    raise ValueError("erreur pas de joeur connu")


def strategy_minmax(grid: State, player: Player) -> Action:
    """call to minmax function"""
    choice: Action = minmax_action(grid, player, 3)[1]
    return choice


def strategy(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    """function to play with a strategy"""
    val = strategy_minmax(state, player)
    return (env, val)


def strategy_random(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    """function to play with a random strat"""
    legits: list[Cell] = legit_moves(state, player)
    value = random.randint(0,len(legits)-1)
    return ({}, legits[value])


def test(iter: int = 1, size: int = 7):
    """test function"""
    tps1 = time.time()
    stats1 = 0
    stats2 = 0
    for _ in range(iter):
        current_player = 1
        env: Environment = {}
        state = create_board(size)
        # possibilité de changer la strategy
        plays = strategy_random(env, state, current_player, 0)[1]
        while final(state):
            state = move(state, plays, current_player)
            if current_player == 1:
                current_player = 2
            else:
                current_player = 1
            if current_player == 1:
                plays = strategy_random(env, state, current_player, 0)[1]
            else:
                plays = strategy(env, state, current_player, 0)[1]
            print_board(state)
        if score(state, 1) == 1:
            stats1 += 1
        elif score(state, 2) == 1:
            stats2 += 1

    print(
        f"temps d'éxécution pour {iter} itérations : {time.time() - tps1:.4f} secondes"
    )
    print(
        f"Nombre de parties gagnées pour le joueur 1: {stats1} {(stats1/iter)*100:.2f}%"
    )
    print(
        f"Nombre de parties gagnées pour le joueur 2: {stats2} {(stats2/iter)*100:.2f}%"
    )


test(iter=1, size=7)
