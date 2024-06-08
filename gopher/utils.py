from typing import Union, Optional
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
Grid = dict[Cell: Player]

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
        key = tuple((pos, val) for pos, val in self.get_grid().items())
        if key in cache and self.is_legit(cache[key][1]):
            return cache[key]
        result = func(self, depth)
        tup: Cell = result[1]
        eval: int = result[0]
        if tup is not None:
            cache[key] = result

            # 12 symmetries
            symmetries = [
                lambda x, y: (x, y),  # Identity
                lambda x, y: (-y, x + y),  # 60° rotation
                lambda x, y: (-(x + y), x),  # 120° rotation
                lambda x, y: (-x, -y),  # 180° rotation
                lambda x, y: (y, -(x + y)),  # 240° rotation
                lambda x, y: (x + y, -x),  # 300° rotation
                lambda x, y: (-x, y),  # Horizontal reflection
                lambda x, y: (x, -y),  # Vertical reflection
                lambda x, y: (-y, -(x + y)),  # 60° rotation + vertical reflection
                lambda x, y: (-(x + y), -y),  # 120° rotation + horizontal reflection
                lambda x, y: (y, x + y),  # 240° rotation + vertical reflection
                lambda x, y: (x + y, y)  # 300° rotation + horizontal reflection
            ]

            for sym in symmetries:
                sym_grid = {sym(x, y): player for (x, y), player in self.get_grid().items()}
                sym_tup = sym(*tup)
                sym_key = tuple((pos, val) for pos, val in sym_grid.items())
                cache[sym_key] = (eval, sym_tup)

        return result

    return memoized_func


def invert_coord_h(cell: Cell) -> Cell:
    return (-cell[0], cell[1])


def invert_coord_v(cell: Cell) -> Cell:
    return (cell[0], -cell[1])


def invert_grid_h(grid: Grid) -> Grid:
    """invert grid horizontally"""
    new_grid: Grid = {}
    for tup in grid:
        new_grid[invert_coord_h(tup)] = grid[tup]
    return new_grid


def invert_grid_v(grid: Grid) -> Grid:
    """invert grid horizontally"""
    new_grid: Grid = {}
    for tup in grid:
        new_grid[invert_coord_v(tup)] = grid[tup]
    return new_grid


def rang(x, y) -> int:
    value: int = 0
    if (x <= 0 and y >= 0) or (y <= 0 and x >= 0):
        value = abs(x) + abs(y)
    elif x < 0 and y < 0:
        value = max(-x, -y)
    else:
        value = max(x, y)
    value = abs(value)
    return value


def rotate_coord(cell: Cell) -> Cell:
    return (-cell[1], cell[0] + cell[1])


def rotate_grid(grid: Grid) -> Grid:
    """rotate grid 60 degrees"""
    new_grid: Grid = {}
    for cell in grid:
        new_grid[rotate_coord(cell)] = grid[cell]
    return new_grid


def sym_coord_transform(coord: Cell, sym_func) -> Cell:
    if sym_func == invert_grid_h:
        return invert_coord_h(coord)
    if sym_func == invert_grid_v:
        return invert_coord_v(coord)
    return coord