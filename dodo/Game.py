"""Fichier pour se connecter à la boucle de jeu et répondre"""

from dodo.dodo_game import DodoGame
from utils.utilitary import (
    Environment,
    Action,
    ActionDodo,
    Player,
    State,
    Time,
)

# NE PAS OUBLIER DE METTRE LE JEU AUQUEL ON JOUE DANS L'ENV


def initialize_dodo(player: Player, hex_size: int, total_time: Time) -> Environment:
    """initializer le jeu"""
    print(f"Temps de la partie : {total_time}")
    game: DodoGame = DodoGame(size=hex_size, starting_player=player)
    # mise à jour de l'environnement
    env: dict = game.to_environnement()
    return env


def strategy_dodo(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    """Joue un coup et le renvoie"""
    print(f"Temps restant : {time_left}")
    # Attention, ici on doit prendre en compte
    # la nouvelle grille et rajouter au tableau déjà existant
    size: int = env["size"]
    starting_player: Player = env["starting"]
    game: DodoGame = DodoGame(size=size, starting_player=starting_player)
    game.restore_env(state, env, player)
    action: ActionDodo = game.strategy_mc(8000)
    game.make_move(action)
    new_env: Environment = game.to_environnement()
    return (new_env, action)
