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
                action = game.strategy_negamax()
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
    print(f"Nombre de parties gagnées pour le joueur 1: {(stats1 / iter) * 100:.2f}%")
    print(f"Nombre de parties gagnées pour le joueur 2: {(stats2 / iter) * 100:.2f}%")



test(10, 4)