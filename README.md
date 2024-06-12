# Project for an AI Course
> Université de Technologie de Compiègne - IA02 : Sylvain Lagrue

This project involved modeling two board games, `Dodo` and `Gopher`, designed by Mark Steere, and creating a program capable of playing them intelligently.

The server was developed by our teacher `Sylvain Lagrue`.

## Gopher Details

> Mypy and Pylint scores are somewhat inaccurate due to module imports and differences between the types `Action` and `Cell`.

The chosen algorithm for playing was Negamax (a variant of Minimax) with caching.

Other implemented and tested algorithms include:
- Minimax
- Alpha-Beta Pruning
- MCTS (Monte Carlo Tree Search)

Depths are chosen automatically.

### Gopher Files

- `./test_gopher`: test our program
- `./gopher/gopher.py`: main file where strategies are implemented
- `./gopher/game.py`: defines how the class will respond to server
- `./gopher/mcts_class.py`: defines MCTS algorithm
- `./gopher/utils.py`: utility functions, data


## Generic Files 
- `./main.py`: connect to server to play
- `./gndclient.py`: client which allows us to connect to a server

## How to run

To run our project, you need to:
- Run the server yourself (which is present in `server/`)
- Run the project using `python main.py 1 "" user`, for instance

To test locally, there is another file named `test_gopher.py` that you can use.

<br/><br/><br/>
> Credits: `leopold.chappuis@etu.utc.fr` `aissa.kadri@etu.utc.fr`