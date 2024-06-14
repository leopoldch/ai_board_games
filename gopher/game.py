"""Fichier pour se connecter à la boucle de jeu et répondre"""

from gopher.gopher import GopherGame
from typing import Union
from gopher.utils import (
    Environment,
    Action,
    Player,
    State,
    Time,
)

# NE PAS OUBLIER DE METTRE LE JEU AUQUEL ON JOUE DANS L'ENV

def initialize_gopher(player: Player, hex_size: int, total_time: Time) -> Environment:
    """initializer le jeu"""
    game: GopherGame = GopherGame(size=hex_size, starting_player=player)
    # mise à jour de l'environnement
    env: dict = game.to_environnement()
    return env


def strategy_gopher(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    """Joue un coup et le renvoie"""
    # Attention, ici on doit prendre en compte la nouvelle grille et rajouter au tableau déjà existant
    size: int = env["size"]
    starting_player: Player = env["starting"]
    game: GopherGame = GopherGame(size=size, starting_player=starting_player)
    game.restore_env(state, env, player)
    action: Action = game.strategy_negamax()
    # print(action)
    game.make_move(action)
    new_env: Environment = game.to_environnement()
    return (new_env, action)
