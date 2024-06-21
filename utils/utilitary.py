"""fichier de fonctions utilitaires"""

from typing import Union
import os

Environment = dict
Cell = tuple[int, int]
ActionGopher = Cell
ActionDodo = tuple[Cell, Cell]
Action = Union[ActionGopher, ActionDodo]
Player = int
State = list[tuple[Cell, Player]]
Score = int
Time = int
Grid = dict[Cell, Player]


# Utilitary functions :


def clear():
    """Efface la console"""
    if os.name == "nt":  # Pour Windows
        os.system("cls")
    else:  # Pour Unix/Linux/MacOS
        os.system("clear")


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


def invert_coord_h(cell: Cell) -> Cell:
    """inversion coord_h"""
    return (-cell[0], -cell[1])


def invert_coord_v(cell: Cell) -> Cell:
    """inversion coord_v"""
    return (cell[1], cell[0])


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


def rotate_coord(cell: Cell) -> Cell:
    """rotate une coordonnée"""
    # (y,-x+y)
    return (cell[1], -cell[0] + cell[1])


def rotate_grid(grid: Grid) -> Grid:
    """rotate grid 60 degrees"""
    new_grid: Grid = {}
    for cell in grid:
        new_grid[rotate_coord(cell)] = grid[cell]
    return new_grid


def rang(x, y) -> int:
    """trouver le rang sur une grille d'une case"""
    value: int = 0
    if x * y <= 0:  # if (x <= 0 and y >= 0) or (y <= 0 and x >= 0):
        value = abs(x) + abs(y)
    elif x < 0 and y < 0:
        value = max(-x, -y)
    else:
        value = max(x, y)
    value = abs(value)
    return value


def do_all_symetries(grid: Grid) -> list[Grid]:
    """Retourne toutes les symétries essentielles"""
    all_grids = []
    already_added = set()

    def add_grid(g: Grid):
        h = tuple(sorted(g.items()))
        if h not in already_added:
            already_added.add(h)
            all_grids.append(g)

    add_grid(grid)
    tmp = grid
    for _ in range(5):
        tmp = rotate_grid(tmp)
        add_grid(tmp)
        add_grid(invert_grid_h(tmp))
        add_grid(invert_grid_v(tmp))
    return all_grids


def get_state_negamax(grid: Grid) -> tuple:
    """Renvoie un state hashable pour negamax"""
    return tuple(sorted(grid.items()))
