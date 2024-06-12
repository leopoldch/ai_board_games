# Game server and python client

WARNING:
- Referee says an action is illegal only checking if cells are in the grid, if enough coordinates and if cells are valid (for dodo and gopher). Does not check if move is legal for DODO
- DoesAction only change the grid, it must also check if there is a winner
- Grid generation for dodo is not perfect (beginning token distribution)

## Features 

- [X] Server state save at each request
- [X] Server resilience to client crash
- [X] Client resilience to server crash
- [X] Waiting of request while other player plays
- [ ] Tournament match maker
- [ ] Documentation
- [X] Client illegal action handling
- [ ] Referee and grid state update
- [ ] Client specifying which game it can play
- [ ] Visualization routes
- [ ] Proper Go

## Todo

- [ ] Refactoring (log vs. error)
- [x] Random players

## Routes

`register`: Request needs to provide `Id` and `Password`. Returns the client `Token` used for other requests.

`start`: start a game or recover an interrupted game (in case of client or server crash).
Request needs to provide client `Token`. Returns game information if the player can play (wait otherwise).

`play`: Do a move. Request needs to provide client `Token` and the `Action`. Returns the other player action and game information
(finished, current game, etc.). The request waits until the other player plays.

## Data format

- Each Group has a token (50 characters)
- Each Match has a token (10 characters)
- When player has an ingoing match, a map (Ingoing) associate the player token with both its color and the match token


## How to launch
Launch client
```
./test_client.py 1 "" toto
```

Start random player:
```
go run ./cmd/server -random -rcolor blue -game gopher
```

If problem, delete `server.json`.