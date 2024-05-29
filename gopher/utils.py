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