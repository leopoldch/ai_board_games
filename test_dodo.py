import time
from dodo.DodoGame import DodoGame


def test(iterations: int, size: int, starting) -> None:
    """fonction de test"""
    score: int = 0
    tps1 = time.time()
    max_val = 0
    for i in range(iterations):
        tps2 = time.time()
        game = DodoGame(size=size, starting_player=starting)
        while game.final():
            #print(game)
            if game.get_player() == 1:
                play = game.strategy_mc(7333)
                game.make_move(play)
                game.set_player(player=2)
            else:
                play = game.strategy_random()
                game.make_move(play)
                game.set_player(player=1)
        # on compte le nombre de parties gagnées par le joueur 1
        if game.get_player() == 1:
            if game.score() == 1:
                score += 1
        else:
            if game.score() == -1:
                score += 1
        temps2: float = time.time() - tps2
        max_val = max(temps2,max_val)
        del game
        print(f"Avancement : {i}  winrate : {(score/(i+1))*100}")

    temps: float = time.time() - tps1
    print()
    print(
        f"Nb itérations : {iterations} | taille : {size} | joueur départ : {starting}"
    )
    print(f"Temps d'éxécution  : {temps:.4f} secondes")
    if iterations > 1:
        print(f"Temps par partie  : {temps/iterations:.4f} secondes. Max : {max_val:.4f} secondes.")
    print(f"Nb de win pour le joueur 1: {score} {(score/iterations)*100:.2f}%")
    print(
        f"Nb de win pour le joueur 2: {iterations-score} {((iterations-score)/iterations)*100:.2f}%"
    )


test(10,4,1)