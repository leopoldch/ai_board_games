#!/usr/bin/python3

#######################################################################
#######################################################################
##############                                       ##################
#############  NE PAS MODIFIER CE FICHIER !!!!!!!!!!  #################
##############                                       ##################
#######################################################################
#######################################################################

VERSION = "gamma"

import time
import ast
from typing import Callable, List, Tuple, Any, Dict, NamedTuple, Union
import requests

Env = Any
Game = int

Cell = tuple[int, int]
ActionGopher = Cell
ActionDodo = tuple[Cell, Cell]  # case de départ -> case d'arrivée
Action = Union[ActionGopher, ActionDodo]
Player = int  # 1 ou 2
State = list[tuple[Cell, Player]]  # État du jeu pour la boucle de jeu
Score = int
Time = int


class GameInfo(NamedTuple):
    game: Game
    player: Player
    clocktime: Time
    state: State
    grid_size: int
    token: str


class FinishInfo(NamedTuple):
    finished: bool
    winner: Player
    final_score: int


InitCallback = Callable[[str, State, Player, int, Time], Env]
StrategyCallback = Callable[[Env, State, Player, Time], Tuple[Env, Action]]
FinalCallback = Callable[[State, Score, Player], None]

GOPHER: Game = 0
DODO: Game = 1

GOPHER_STR: str = "gopher"
DODO_STR: str = "dodo"

EMPTY: Player = 0
RED: Player = 1
BLUE: Player = 2

CODE_ILLEGAL_ACTION = 310


class IllegalActionException(Exception):
    pass


def _convert_grid_to_py(grid: dict) -> Tuple[State, int]:
    """Convert the grid received from go server to python format

    Args:
        grid (dict): Grid as JSON

    Returns:
        Tuple[State, int]: Grid as list of tuple(Cell, Player), and size of the grid
    """
    size = grid["Size"]
    grid_map = grid["Grid"]
    grid_py = [(ast.literal_eval(key), value) for key, value in grid_map.items()]
    return grid_py, size


emptyRequest = {
    "Token": "",
    "PossibleGames": [],
    "Id": 0,
    "Members": "",
    "Password": "",
    "Action": [],
}


def _do_request(
    session: requests.Session, basename: str, command: str, data: Dict[str, Any]
) -> Dict[str, Any]:
    # print(f"Doing request {command} with data {data}")
    try_again = True
    while try_again:
        try_again = False
        try:
            req = session.post(
                f"{basename}/{command}",
                json=data,
                headers={"Content-Type": "application/json"},
            )
        except requests.exceptions.ConnectionError:
            try_again = True
            time.sleep(2)
            print("Server unavailable, retrying...")

    if req.status_code == CODE_ILLEGAL_ACTION:
        raise IllegalActionException()

    if req.status_code != requests.codes["ok"]:
        print(f"Request error: {req.text}")
        req.raise_for_status()

    answer = req.json()
    return answer


def _connect(
    session: requests.Session,
    basename: str,
    group: str,
    members: str,
    password: str,
    possible_games: List[Game],
) -> str:
    """Connect the client to the server

    Args:
        session (requests.Session): Session handler
        basename (str): Basename of the API
        group (str): Id of the group
        members (str): Members of the group
        password (str): Password of the group

    Returns:
        str: Connection token
    """
    data = emptyRequest.copy()
    data["Id"] = int(group)
    data["Members"] = str(members)
    data["Password"] = str(password)
    data["PossibleGames"] = possible_games

    resp = _do_request(session, basename, "register", data)
    return resp["Token"]


def _request_game_info(
    session: requests.Session, basename: str, token: str
) -> GameInfo:
    data = emptyRequest.copy()
    data["Token"] = token

    resp = _do_request(session, basename, "start", data)
    # Bloquant si 2ème joueur
    # Spécifier à quel jeux ont joue
    grid, size = _convert_grid_to_py(resp["Grid"])
    info = GameInfo(
        resp["Game"], resp["Player"], resp["Clocktime"], grid, size, resp["MatchToken"]
    )

    return info


def _wait_my_turn(
    session: requests.Session, basename: str, token: str, action: Action
) -> Tuple[GameInfo, FinishInfo]:
    data = emptyRequest.copy()
    data["Token"] = token
    if isinstance(action[0], int):  # Missing a level of tuple
        data["Action"] = [str(tuple(tpl for tpl in action if not tpl is None))]
    else:
        data["Action"] = [str(tpl) for tpl in action if not tpl is None]

    resp = _do_request(session, basename, "play", data)

    # if resp["end"] != 0:
    #     return (), resp["end"]
    grid, size = _convert_grid_to_py(resp["Grid"])
    game_info = GameInfo(
        resp["Game"], resp["Player"], resp["Clocktime"], grid, size, resp["MatchToken"]
    )
    finish_info = FinishInfo(resp["Finished"], resp["Winner"], resp["FinalScore"])

    return game_info, finish_info


def game_to_str(game: Game) -> str:
    if game == DODO:
        return DODO_STR
    return GOPHER_STR


def str_to_game(game: str) -> Game:
    if game == DODO_STR:
        return DODO
    return GOPHER


def cell_to_grid(cell: Cell, hex_size: int) -> tuple[int, int]:
    return (
        2 * hex_size - 1 - cell[0] - cell[1],
        3 * hex_size - 1 + 3 * cell[0] - 3 * cell[1],
    )


def empty_grid(hex_size: int) -> list[list[str]]:
    grid = [[" "] * (hex_size * 6 - 1) for _ in range(4 * hex_size - 1)]

    for row in range(-hex_size + 1, hex_size):
        for col in range(
            max(row - hex_size + 1, -hex_size + 1),
            min(row + hex_size - 1, hex_size - 1) + 1,
        ):
            i, j = cell_to_grid((row, col), hex_size)
            grid[i - 1][j] = "_"
            grid[i + 1][j] = "_"
            grid[i - 1][j + 1] = "_"
            grid[i + 1][j + 1] = "_"
            grid[i][j - 1] = "/"
            grid[i + 1][j - 1] = "\\"
            grid[i][j + 2] = "\\"
            grid[i + 1][j + 2] = "/"

    return grid


def grid_state(state: State, hex_size: int) -> str:
    grid = empty_grid(hex_size)
    for cell, player in state:
        x, y = cell_to_grid(cell, hex_size)
        if player == RED:
            grid[x][y] = "R"
        elif player == BLUE:
            grid[x][y] = "B"
        else:
            grid[x][y] = " "
    return "\n".join("".join(c for c in line) for line in grid)


def start(
    server_name: str,
    group: str,
    members: str,
    password: str,
    possible_games: List[str],
    init: InitCallback,
    strategy: StrategyCallback,
    end: FinalCallback,
    gui: bool = True,
):
    basename = server_name
    basename = basename.strip("/")

    session = requests.Session()

    token = _connect(
        session,
        basename,
        group,
        members,
        password,
        [str_to_game(g) for g in possible_games],
    )
    print("Connected, requesting next game")
    game_info = _request_game_info(session, basename, token)

    # Call of initialization client function
    env = init(
        game_to_str(game_info.game),
        game_info.state,
        game_info.player,
        game_info.grid_size,
        game_info.clocktime,
    )
    finish_info = FinishInfo(False, 0, 0)
    while not finish_info.finished:
        if gui:
            print(grid_state(game_info.state, game_info.grid_size))
        # Call of strategy client function
        newenv, action = strategy(
            env, game_info.state, game_info.player, game_info.clocktime
        )
        # Send action to the server, will wait for other player to play
        try:
            game_info, finish_info = _wait_my_turn(session, basename, token, action)
            env = newenv
        except IllegalActionException:
            print("Illegal action!")

    # Call of final callback to give results
    end(game_info.state, finish_info.final_score, finish_info.winner)
