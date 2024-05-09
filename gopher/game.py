from board import *
from player import *

# Types de base utilisés par l'arbitre
Environment = ... # Ensemble des données utiles (cache, état de jeu...) pour
                  # que votre IA puisse jouer (objet, dictionnaire, autre...)
Cell = tuple[int, int]
ActionGopher = Cell
ActionDodo = tuple[Cell, Cell] # case de départ -> case d'arrivée
PlayerType = int # 1 ou 2
State = list[tuple[Cell, PlayerType]] # État du jeu pour la boucle de jeu
Score = int
Time = int


class Gopher:

    def __init__(self, size : int) -> None:
        """initialise l'objet du jeu Gopher"""
        
        self.__round : int = 0
        
        # setup les joueurs grâce aux classes déjà implémentées 
        self.__player1 : Player  = Player(1)
        self.__player2 : Player = Player(2)

        # setup le plateau 
        self.__board : Board = Board(size)

        self.__total_time : Time = 0
    
    def final_result(state: State, score: Score, player: PlayerType) -> None:
        """print le résultat final"""
        pass

