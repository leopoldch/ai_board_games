from board import *
from player import *
from cache import *
from typing import Union

# Types de base utilisés par l'arbitre

Environment = Cache
Cell = tuple[int, int]
ActionGopher = Cell
ActionDodo = tuple[Cell, Cell] # case de départ -> case d'arrivée
Action = Union[ActionGopher, ActionDodo]
Player = int # 1 ou 2
State = list[tuple[Cell, Player]] # État du jeu pour la boucle de jeu
Score = int
Time = int



class Gopher:

    def __init__(self, size : int) -> None:
        """initialise l'objet du jeu Gopher"""
        
        self.__round : int = 0
        
        # setup les joueurs grâce aux classes déjà implémentées 
        self.__player1 : PlayerClass  = Player(1)
        self.__player2 : PlayerClass = Player(2)

        # setup le plateau 
        self.__board : Board = Board(size)

        self.__total_time : Time = 0
    

    def final_result(state: State, score: Score, player: PlayerClass) -> None:
        """print le résultat final"""
        pass

