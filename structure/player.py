"""file to define the structure of the players and its behavior"""

class Player:
    """represents the player"""

    def __init__(self) -> None:
        """constructeur du joueur"""
        self.__score : int = 0
        self.__strategy = callable
    
