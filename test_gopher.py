"""Fichier de test pour gopher"""

import time
from gopher.gopher_game import GopherGame
from utils.utilitary import (
    Player,
    Action
)


def test(iterations: int, size: int, starting: Player) -> None:
    """fonction de test"""
    score: int = 0
    tps1 = time.time()
    play: Action
    max_val : float = 0
    for i in range(iterations):
        tps2 = time.time()
        game = GopherGame(size=size, starting_player=starting)
        while game.final():
            # print(game)
            if game.get_player() == 1:
                play = game.strategy_random()
                game.make_move(play)
                game.set_player(player=2)
            else:
                play = game.strategy_negamax()
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
        max_val = max(temps2, max_val)
        print(
            f"itération : {i} | pourcentage de victoire joueur 1 : {(score/(i+1))*100:.2f}%"
        )
        print(f"Temps d'éxécution : {temps2:.2f}")
    temps: float = time.time() - tps1
    print()
    print(
        f"Nb itérations : {iterations} | taille : {size} | joueur départ : {starting}"
    )
    print(f"Temps d'éxécution  : {temps:.4f} secondes")
    if iterations > 1:
        print(
            f"Temps par partie  : {temps/iterations:.4f} secondes. Max : {max_val:.4f} secondes."
        )
    print(f"Nb de win pour le joueur 1: {score} {(score/iterations)*100:.2f}%")
    print(
        f"Nb de win pour le joueur 2: {iterations-score} {((iterations-score)/iterations)*100:.2f}%"
    )


if __name__ == "__main__":
    test(iterations=100, size=6, starting=1)
    # utlimate_test(200,4,11)
