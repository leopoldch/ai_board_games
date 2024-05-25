from board import *
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


class PlayerClass:
    """classe joueur"""

    def __init__(self, id : PlayerType) -> None:
        """initialise l'objet Player"""
        self.__id = id
        self.__score = 0
    
    def get_id(self) -> PlayerType:
        """getter id"""
        return self.__id
    
    def get_score(self) -> int:
        """getter score"""
        return self.__score

    def add_score(self) -> None:
        """adds 1 to current score"""
        self.__score+=1

    def strategy(env: Environment, state: State, player: PlayerType,
             time_left: Time) -> tuple[Environment, Action]:
        """strategy how to play"""
        


