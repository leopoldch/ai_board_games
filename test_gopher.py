"""Fichier de test"""

import time
import math
from gopher.gopher import GopherGame
from gopher.utils import (
    clear, 
    Player,
    Cell,
    do_all_symetries,    
)

def test(iterations: int, size: int, starting: Player) -> None:
    """fonction de test"""
    score: int = 0
    tps1 = time.time()
    play : Cell
    max_val = 0
    for i in range(iterations):
        if iterations > 1:
            clear()
            print("Avancement : ", end=" ")
            compteur: int = math.ceil((i / iterations) * 100)
            print("[" + compteur * "-" + ((100 - compteur) * " " + "]"))
        tps2 = time.time()
        game = GopherGame(size=size, starting_player=starting)
        while game.final():
            #print(game)
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
        temps2: float = time.time() - tps2
        max_val = max(temps2,max_val)
        del game

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



def utlimate_test(iterations: int, fr : int, to : int) -> None:
    """get stats for every game"""
    result = f"NOMBRE D'ITERATIONS PAR SIZE ET PAR SIDE DE DEPART : {iterations}\n"
    result += "JOUEUR 1 NEGAMAX - JOUEUR 2 RANDOM\n\n"
    result += "=========================================\n"
    for size in range(fr,to):
        result+="\n"
        score: int = 0
        tps1 = time.time()
        play : Cell
        max_val = 0
        for _ in range(iterations):
            tps2 = time.time()
            game = GopherGame(size=size, starting_player=1)
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
            temps2: float = time.time() - tps2
            max_val = max(temps2,max_val)
            del game
        temps: float = time.time() - tps1
        result+=f"taille : {size}\n"
        result+=f"Temps d'éxécution  : {temps:.4f} secondes\n"
        result+=f"Temps par partie  : {temps/iterations:.4f} secondes. Max : {max_val:.4f} secondes.\n"
        result+=f"Nb de win pour le joueur 1: {score} {(score/iterations)*100:.2f}%\n"
        result+=f"Nb de win pour le joueur 2: {iterations-score} {((iterations-score)/iterations)*100:.2f}%\n"
    result += "\n\n\nJOUEUR 2 NEGAMAX - JOUEUR 1 RANDOM\n\n"
    result += "=========================================\n"
    for size in range(fr,to):
        result+="\n"
        score: int = 0
        tps1 = time.time()
        play : Cell
        max_val = 0
        for _ in range(iterations):
            tps2 = time.time()
            game = GopherGame(size=size,starting_player=1)
            while game.final():
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
            max_val = max(temps2,max_val)
            del game
        temps: float = time.time() - tps1
        result+=f" taille : {size}\n"
        result+=f"Temps d'éxécution  : {temps:.4f} secondes\n"
        result+=f"Temps par partie  : {temps/iterations:.4f} secondes. Max : {max_val:.4f} secondes.\n"
        result+=f"Nb de win pour le joueur 1: {score} {(score/iterations)*100:.2f}%\n"
        result+=f"Nb de win pour le joueur 2: {iterations-score} {((iterations-score)/iterations)*100:.2f}%\n"

    with open("stats.txt",'w+') as file:
        file.write(result)


if __name__ == "__main__":
    #test(iterations=20, size=10, starting=2)
    utlimate_test(200,4,11)
