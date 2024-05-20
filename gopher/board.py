"""file to define the structure of the board and its behavior"""
import math

# Types de base utilisés par l'arbitre
Environment = ... # Ensemble des données utiles (cache, état de jeu...) pour
                  # que votre IA puisse jouer (objet, dictionnaire, autre...)
Cell = tuple[int, int]
ActionGopher = Cell
ActionDodo = tuple[Cell, Cell] # case de départ -> case d'arrivée
Player = int # 1 ou 2
State = list[tuple[Cell, Player]] # État du jeu pour la boucle de jeu
Score = int
Time = int


# utilitary fonctions to make the code more readable

def str_red(text: str) -> str:
    """Colors text, red"""
    return "\033[31m" + text + "\033[0m"


def str_blue(text: str) -> str:
    """Colors text, red"""
    return "\033[34m" + text + "\033[0m"


# ======================= grid template =======================
# documentation https://www.redblobgames.com/grids/hexagons/#map-storage


class Board:
    """board grid structure and behavior"""

    def __init__(self, size: int) -> None:
        """initialize the grid"""

        if size < 6:
            raise ValueError("La grille ne peut pas être inférieure à 6 ")
        
        self.__grid : dict[Cell:int] ={} # stocke l'état de la grille
        self.__size = size # dimensions de la grille
        self.__firstmove = True
        
        # variables pour initialiser l'hexagone
        counter: int = math.ceil(self.__size / 2)
        start = [0, math.floor(self.__size/2)]
        verif: bool = True
        iterations: int = self.__size

        if self.__size % 2 == 0:
            iterations += 1
        for _ in range(iterations):
            if counter == self.__size:
                verif = False
            if verif:
                for i in range(counter):
                    cell : Cell = (start[0]+i,start[1])
                    self.__grid[cell] = 0
                counter += 1
                start = [start[0]-1,start[1]-1]
            else:
                for i in range(counter):
                    cell : Cell = (start[0]+i,start[1])
                    self.__grid[cell] = 0
                counter -= 1
                start = [start[0],start[1]-1]

    def __str__(self) -> str:
        """print function"""
        returned_str: str = ""
        
        # variables pour initialiser l'hexagone
        counter: int = math.ceil(self.__size / 2)
        start = [0, math.floor(self.__size/2)]
        verif: bool = True
        iterations: int = self.__size

        if self.__size % 2 == 0:
            iterations += 1
        for _ in range(iterations):

            if counter == self.__size:
                verif = False

            if verif:
                returned_str += " "*(self.__size-counter)
                for i in range(counter):
                    cell : Cell = (start[0]+i,start[1])
                    case : int = self.__grid[cell]
                    if case == 1:
                        returned_str += f"{str_red("*")} "
                    elif case == 2:
                        returned_str += f"{str_blue("*")} "
                    else:
                        returned_str += "* "
                returned_str +="\n"
                counter += 1
                start = [start[0]-1,start[1]-1]
            else:
                returned_str += " "*(self.__size-counter)
                for i in range(counter):
                    cell : Cell = (start[0]+i,start[1])
                    case : int = self.__grid[cell]
                    if case == 1:
                        returned_str += f"{str_red("*")} "
                    elif case == 2:
                        returned_str += f"{str_blue("*")} "
                    else:
                        returned_str += "* "
                returned_str +="\n"
                counter -= 1
                start = [start[0],start[1]-1]
        return returned_str

    def get_neighbors(self, x: int, y: int) -> list[Cell]:
        """returns coordonates of neighbors"""
        max : int = math.floor(self.__size/2)

        if  x > max or x < -max or y > max or y< -max :
            raise ValueError("Case non dans le tableau")
        
        neighbors: list[Cell] = []
        closes: tuple[int, int, int] = (-1, 0, 1)

        for value_x in closes:
            for value_y in closes:
                vx: int = x + value_x
                vy: int = y + value_y
                if (
                    -max <= vx <= max
                    and -max <= vy <= max
                    and (vx, vy) != (x, y)
                    and (value_x,value_y) != (1,-1)
                    and (value_x,value_y) != (-1,1)
                ):

                    key : Cell = (vx,vy)    
                    if key in self.__grid.keys():
                        stored_value = self.__grid[key]
                        if stored_value != -1 and key not in neighbors:
                            neighbors.append(key)

        return neighbors
    
    def is_legit(self, start: Cell, player : Player) -> bool:
        """returns if move is legit or not"""


        # si la case est déjà occupée on retourne faux
        if self.__grid[start] != 0:
            return False
        
        # attention si la grille est vide alors le premier coup est valide
        # pour réduire la compléxité on peut ajouter un attribut de classe premier coup

        if self.__firstmove:
            return True

        neighbors: list[Cell] = self.get_neighbors(start[0], start[1])
        verif : int = 0
        
        for item in neighbors:
            if self.__grid[(item[0],item[1])] == player:  # vérification s'il y a un piont du joueur adjascent
                return False
            # vérification s'il y a exactement un seul piont ennemy adjascent
            if player == 1:
                if self.__grid[(item[0], item[1])] == 2: 
                    verif += 1
            elif player == 2 :
                if self.__grid[(item[0], item[1])] == 1:
                    verif += 1
        if verif == 1:
            return True
        return False

    def legit_moves(self, player : Player) -> list[Cell]:
        """returns legit moves"""
        results : list[Cell] = []
        for item in self.__grid.items():
            if item[1] == 0 and self.is_legit(item[0],player):
                results.append(item[0])
        return results

    def move(self, cell : Cell, player : Player) -> None:
        """function to allow users to place new items on boards following rules"""
        if not self.is_legit(cell, player):
            raise ValueError("Impossible de bouger ce pion à cet endroit")
        else:
            # on place le pion
            self.__grid[cell] = player
            # met à jour que le premier coup a été joué 
            if self.__firstmove:
                self.__firstmove = False

