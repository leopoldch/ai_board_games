import math

class Board: 

    def __init__(self, size:int) -> None:
        # attributs de la classe
        self.__grid : list = []
        self.__size : int = size
        
        # variables pour initialiser l'hexagone
        counter:int = math.ceil(self.__size/2)
        verif: bool = True
        tab : list[int]

        iterations : int = self.__size
        if self.__size %2 == 0:
            iterations +=1

        for i in range(iterations):
            tab : list[int] = []
            if counter == self.__size:
                verif = False
                
            if verif:
                for j in range(self.__size-counter):
                    tab.append(-1)
                for j in range(counter):
                    tab.append(0)
                counter+=1
            else:
                for j in range(counter):
                    tab.append(0)
                for j in range(self.__size-counter):
                    tab.append(-1)
                counter-=1
            self.__grid.append(tab)

    def __str__(self):
        returned_str : str = ""

        parsing_correction: int
        
        for tab in self.__grid:
            parsing_correction = tab.count(-1)
            returned_str += parsing_correction*"  "
            for value in tab:
                if value != -1:
                    returned_str += f" {value} "
            returned_str += "\n"
        return returned_str

    def get_emplacement(self, player : int) -> list[tuple[int,int]]:
        pass
    
    def get_neighbors(self, x :int,y :int) -> list[tuple[int,int]]:
        pass

    def legit_moves(self, start : tuple[int,int]) -> list[tuple[int,int]]:
        pass    

    def move_case(self, start : tuple[int,int], dest : tuple[int,int]):
        pass


test = Board(7)
print(test)