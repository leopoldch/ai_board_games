"""Fichier pour se connecter à la boucle de jeu et répondre"""
from gopher.gopher import GopherGame

Environment = dict
Cell = tuple[int, int]
ActionGopher = Cell
Player = int
State = list[tuple[Cell, Player]]
Score = int
Time = int
Grid = dict[Cell, Player]

# Ne pas oublier de mettre le nom du jeu en dans l'environnement 

def initialize_gopher(player: Player, hex_size: int, total_time: Time) -> Environment:
    """initializer le jeu"""
    game : GopherGame = GopherGame(size=hex_size,starting_player=player)
    # mise à jour de l'environnement 
    env : dict = game.to_environnement()
    return env
    

def strategy_gopher(env: Environment, state: State, player: Player,time_left: Time) -> tuple[Environment, ActionGopher]:
    """Joue un coup et le renvoie"""
    # Attention, ici on doit prendre en compte la nouvelle grille et rajouter au tableau déjà existant 
    size : int = env['size']
    starting_player : Player = env['starting']
    game : GopherGame = GopherGame(size=size, starting_player=starting_player)
    game.restore_env(state,env, player)
    action :  ActionGopher = game.strategy_negamax()
    game.make_move(action)
    new_env : Environment = game.to_environnement()
    return (new_env,action)
     
    
