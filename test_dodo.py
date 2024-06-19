import time
from dodo.DodoGame import DodoGame


def test(iter: int, size: int):
    """test function"""
    tps1 = time.time()
    stats1 = 0
    stats2 = 0
    for _ in range(iter):
        starting_player = 1
        game = DodoGame(size, starting_player)

        while game.final():
            if game.get_player() == 1:
                action = game.strategy_mcts()
            else:
                action = game.strategy_random()

            game.make_move(action)
            game.set_player(3 - game.get_player()) 

        score = game.score()
        if score == 1:
            if game.get_player() == 1: 
                stats1 += 1
            else:
                stats2 += 1

    print(f"Temps d'exécution pour {iter} itérations : {time.time() - tps1:.4f} secondes")
    print(f"Temps d'exécution pour une partie : {(time.time() - tps1)/iter:.4f} secondes")
    print(f"Nombre de parties gagnées pour le joueur 1: {(stats1 / iter) * 100:.2f}%")
    print(f"Nombre de parties gagnées pour le joueur 2: {(stats2 / iter) * 100:.2f}%")

def test_mcts_win_rate(num_games: int, mcts_player) -> float:
    wins = 0
    start_time = time.time()
    for _ in range(num_games):
        game = DodoGame(size=4, starting_player=1)
        current_player = game.get_player()

        while game.final():
            if current_player == mcts_player:
                action = game.strategy_mc()
            else:
                action = game.strategy_random()

            game.make_move(action)
            current_player = 3 - current_player

        if game.score() == 1:
            if game.get_player() == current_player:
                wins += 1

    end_time = time.time()
    elapsed_time = end_time - start_time
    win_rate = (wins / num_games) * 100
    print(f"win rate : {win_rate}%")
    print(f"temps : {elapsed_time} ")


test_mcts_win_rate(100,1)


#test(10, 4)