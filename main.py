"""Main file wich connects to server and play"""

import argparse
from typing import Dict, Any
from gndclient import start, Action, Score, Player, State, Time, DODO_STR, GOPHER_STR
from gopher.game import initialize_gopher, strategy_gopher

Environment = Dict[str, Any]


def initialize(
    game: str, state: State, player: Player, hex_size: int, total_time: Time
) -> Environment:
    """initialise l'environnement"""
    print("Init")
    print(
        f"{game} you play {player} on a grid of size {hex_size}. Time remaining: {total_time}"
    )
    if game == "gopher":
        env = initialize_gopher(player=player, hex_size=hex_size, total_time=total_time)
        return env

    # Sinon Dodo -> A IMPLEMENTER
    # pas besoin de else ou elif après return
    # state de départ à utiliser dans dodo


def strategy_brain(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    """fonction de stratégie"""
    print(f"Temps restant : {time_left}")
    if env["game"] == "gopher":
        values: tuple[Environment, Action] = strategy_gopher(
            env, state, player, time_left
        )
        return values

    # Sinon Dodo -> A IMPLEMENTER
    # pas besoin de else ou elif après return


def final_result(state: State, score: Score, player: Player):
    """affichage du gagnant"""
    print(f"Ending: {player} wins with a score of {score}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="ClientTesting", description="Test the IA02 python client"
    )

    parser.add_argument("group_id")
    parser.add_argument("members")
    parser.add_argument("password")
    parser.add_argument("-s", "--server-url", default="http://lchappuis.fr:8080/")
    parser.add_argument("-d", "--disable-dodo", action="store_false")
    parser.add_argument("-g", "--disable-gopher", action="store_false")
    args = parser.parse_args()

    available_games = []
    if not args.disable_dodo:
        available_games.append(DODO_STR)
    if not args.disable_gopher:
        available_games.append(GOPHER_STR)

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
