"""Main file wich connects to server and play"""

import argparse
from typing import Dict, Any
from utils.gndclient import (
    start,
    Action,
    Score,
    Player,
    State,
    Time,
    DODO_STR,
    GOPHER_STR,
)
from gopher.game import initialize_gopher, strategy_gopher
from dodo.game import initialize_dodo, strategy_dodo

Environment = Dict[str, Any]


def initialize(
    game: str, _, player: Player, hex_size: int, total_time: Time
) -> Environment:
    """initialise l'environnement"""
    print(f"{game} you play {player} on a grid of size {hex_size}.")
    if game == "gopher":
        env = initialize_gopher(player=player, hex_size=hex_size, total_time=total_time)
        return env
    env = initialize_dodo(player=player, hex_size=hex_size, total_time=total_time)
    return env


def strategy_brain(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    """fonction de stratégie"""
    values: tuple[Environment, Action]
    if env["game"] == "gopher":
        values = strategy_gopher(
            env, state, player, time_left
        )
        print("coup joué")
        return values
    values = strategy_dodo(env, state, player, time_left)
    print("coup joué")
    return values


def final_result(_, score: Score, player: Player):
    """affichage du gagnant"""
    print(f"Ending: {player} wins with a score of {score}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="ClientTesting", description="Test the IA02 python client"
    )

    parser.add_argument("group_id")
    parser.add_argument("members")
    parser.add_argument("password")
    parser.add_argument("-s", "--server-url", default="http://localhost:8080")
    parser.add_argument("-d", "--disable-dodo", action="store_true")
    parser.add_argument("-g", "--disable-gopher", action="store_true")
    args = parser.parse_args()

    available_games = [DODO_STR, GOPHER_STR]
    if args.disable_dodo:
        available_games.remove(DODO_STR)
    if args.disable_gopher:
        available_games.remove(GOPHER_STR)

    start(
        args.server_url,
        args.group_id,
        args.members,
        args.password,
        available_games,
        initialize,
        strategy_brain,
        final_result,
        gui=True,
    )
