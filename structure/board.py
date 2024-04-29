"""file to define the structure of the board and its behavior"""

import math

# ======================= grid template =======================
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
        if size < 2:
            raise ValueError("La taille de la grille ne peut pas être inférieure à 2")

        self.__grid: list[list] = []
        self.__size: int = size

        # variables pour initialiser l'hexagone
        counter: int = math.ceil(self.__size / 2)
        verif: bool = True
        tab: list[int]

        iterations: int = self.__size
        if self.__size % 2 == 0:
            iterations += 1

        for _ in range(iterations):
            tab  = []
            if counter == self.__size:
                verif = False

            if verif:
                for _ in range(self.__size - counter):
                    tab.append(-1)
                for _ in range(counter):
                    tab.append(0)
                counter += 1
            else:
                for _ in range(counter):
                    tab.append(0)
                for _ in range(self.__size - counter):
                    tab.append(-1)
                counter -= 1
            self.__grid.append(tab)

        # on fini par placer les jetons des deux joueurs sur la grille :
        self.init_items_on_board()

    def __str__(self) -> str:
        """print function"""
        returned_str: str = ""
        for tab in self.__grid:
            returned_str += " " * tab.count(-1)
            for number in tab:
                if number == 1:
                    returned_str += str_red("*") + " "
                elif number == 2:
                    returned_str += str_blue("*") + " "
                elif number == 0:
                    returned_str += "*" + " "
                elif number == -1:
                    pass
                else:
                    raise ValueError("Valeur incorrecte dans les données de la grille")
            returned_str += "\n"
        return returned_str

    def init_items_on_board(self):
        """init items inside the grid"""
        value : int = self.__size - self.__grid[0].count(-1)
        items : list = []
        
        # remplir le tableau items avec les éléments à laisser neutres 

        for i in range(self.__size):
            for j in range(self.__size):
                # mettre à jour la grid pour bien positionner les items 
                pass


    def get_emplacement(self, player: int) -> list[tuple[int, int]]:
        """returns all emplacements of a player"""
        emplacements: list[tuple[int, int]] = []
        for i in range(self.__size):
            for j in range(self.__size):
                if self.__grid[i][j] != -1 and self.__grid[i][j] == player:
                    emplacements.append((i, j))
        return emplacements

    def get_neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        """returns coordonates of neighbors"""
        if x > self.__size - 1 or y >= self.__size or x < 0 or y < 0:
            raise ValueError("Case doesn't exists")

        neighbors: list[tuple[int, int]] = []
        closes: tuple[int, int, int] = (-1, 0, 1)
        for value_x in closes:
            for value_y in closes:
                vx: int = x + value_x
                vy: int = y + value_y
                if (
                    -1 <vx <= self.__size - 1
                    and -1 <vy <= self.__size - 1
                    and (vx, vy) != (x, y)
                ):
                    stored_value = self.__grid[vx][vy]
                    if stored_value != -1 and (vx, vy) not in neighbors:
                        neighbors.append((vx, vy))

        return neighbors

    def legit_move_for_case(self, start: tuple[int, int]) -> list[tuple[int, int]]:
        """returns legit moves"""
        legits_moves: list[tuple[int, int]] = []
        neighbors: list[tuple[int, int]] = self.get_neighbors(start[0], start[1])
        for item in neighbors:
            if self.__grid[item[0]][item[1]] == 0:  # case innocupée
                legits_moves.append(item)
        return legits_moves

    def move_case(self, start: tuple[int, int], dest: tuple[int, int]) -> None:
        """Move item if it is possible"""
        if dest not in self.legit_move_for_case(start):
            raise ValueError("Impossible de bouger cette case à cet endroit")

        self.__grid[dest[0]][dest[1]] = self.__grid[start[0]][start[1]]
        self.__grid[start[0]][start[1]] = 0  # on libère la case


test = Board(7)
print(test)
