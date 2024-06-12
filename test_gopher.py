"""Fichier de test"""

import time
import math
from gopher.gopher import GopherGame
from gopher.utils import clear, Action, Player,Cell


def test(iterations: int, size: int, starting: Player) -> None:
    """fonction de test"""
    score: int = 0
    tps1 = time.time()
    play : Cell
    for i in range(iterations):
        if iterations > 1:
            clear()
            print("Avancement : ", end=" ")
            compteur: int = math.ceil((i / iterations) * 100)
            print("[" + compteur * "-" + ((100 - compteur) * " " + "]"))
        game = GopherGame(size=size, starting_player=starting)
        while game.final():
            if game.get_player() == 1:
                play = game.strategy_negamax()
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
        del game

    temps: float = time.time() - tps1
    print()
    print(
        f"Nb itérations : {iterations} | taille : {size} | joueur départ : {starting}"
    )
    print(f"Temps d'éxécution  : {temps:.4f} secondes")
    if iterations > 1:
        print(f"Temps par partie  : {temps/iterations:.4f} secondes")
    print(f"Nb de win pour le joueur 1: {score} {(score/iterations)*100:.2f}%")
    print(
        f"Nb de win pour le joueur 2: {iterations-score} {((iterations-score)/iterations)*100:.2f}%"
    )


test(iterations=1, size=3, starting=2)
