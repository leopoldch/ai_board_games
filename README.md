# Project for an AI Course
> Université de Technologie de Compiègne - IA02

This project involved modeling two board games, `Dodo` and `Gopher`, designed by Mark Steere, and creating a program capable of playing them intelligently.

> Pylint scores are somewhat inaccurate due to module imports. To avoid getting import errors I disabled them in `.pylintrc`

## Gopher Details

The chosen algorithm for playing was Negamax (a variant of Minimax) with caching.

Other implemented and tested algorithms:
- Minimax
- Alpha-Beta
- Monte Carlo Tree Search

Depths are chosen automatically using another hashtable. After a certain amount of played moves, depth is increased in order to find a winning path.

```
def __negamax_depth(self) -> int:
    """depth for negamax"""
    if self.__size <= 3:
        return 100000
    if self.__size == 6 and len(self.__played) > 11:
        if self.__neg_update:
            print("updaté")
            self.__negamax_cache = {}
            self.__neg_update = False
        return 9
    depths: dict[int, int] = {4: 1000, 5: 12, 6: 7, 7: 7, 8: 6, 9: 5, 10: 4}
    return depths.get(self.__size, 3)
```

The winning strategy for player 1 on odd-numbered grids is implemented in O(1) time with a simple direction calculation
```
if (
    length > 1
    and self.__starting == self.__current_player
    and self.__size % 2 == 1
):
    length -= 1
    next_cell: Cell = self.get_direction()
    if next_cell in self.__legits:
        return next_cell
```
> The calculation is done in self.get_diraction() and is indeed very basic

The first moves for player 1 are fixed depending of the size. `(0,0)` or `(0,size-1)`

```
if self.__firstmove and self.__size % 2 == 1:
            return (0, 0)
        if self.__firstmove and self.__size % 2 == 0:
            return (0, self.__size - 1)
```

### Why did we choose Negamax?

Negamax is a simplified version of Minimax where the same function is used for both players by inverting the score. 
This makes the implementation easier and more efficient.

- On a grid of size 4, the Negamax algorithm can solve the game from the start.
- On a grid of size 6 with a fixed depth of 9 against a random opponent, the win rate over 200 iterations is `100%` in a reasonable time (on average less than 60 seconds per game).


### Gopher Files

- `./test_gopher`: test our program
- `./gopher/gopher_game.py`: main file where strategies are implemented
- `./gopher/game.py`: defines how the class will respond to server

## Dodo Details

The chosen algorithm for playing was Monte Carlo (MC).

Other implemented and tested algorithms:
- Negamax
- MCTS (Monte Carlo Tree Search)

### Why did we choose the Monte Carlo algorithm?

- We chose to keep an algorithm like MC or MCTS because we get the best results. From observations over a large number of iterations, simulation algorithms perform better when faced with a large number of possible moves than depth-first search algorithms. The explanation might be that simulations can be fixed to a specific number or time, whereas depth-first search explodes node after node.
- Our idea was to combine the MC algorithm for the beginning of the game and then switch to Negamax after a certain number of moves. This would have allowed us to find an optimal solution without costing too much in performance. After implementation, the results were good but not as good as with an MC ~8000 iterations.
- Win rate against a random opponent with the MC algorithm (~8000 iterations): `100%`

### Dodo Files

- `./test_dodo`: test our program 
- `./dodo/dodo_game.py`: main file where strategies are implemented
- `./dodo/game.py`: defines how the class will respond to server

## Generic Files 
- `./main.py`: connect to server to play
- `./utils/gndclient.py`: client which allows us to connect to a server
- `./utils/utilitary.py`: utility functions, data

## How to run

To run our project, you need to:
- Run the server yourself (which is present in `server/`)
- Run the project using `python main.py 1 "" user`, for instance
- Modify the server url in `main.py` 
  - `parser.add_argument("-s", "--server-url", default="http://server.url:8080")`

To test locally, there is another file named `test_gopher.py` (resp `test_dodo.py`) that you can use.

<br/><br/><br/>
> Credits: `leopold.chappuis@etu.utc.fr` `aissa.kadri@etu.utc.fr`
