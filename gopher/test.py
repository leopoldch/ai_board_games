from gopher import *

def test(iter: int, size: int, depth: int,starting : Player) -> None:
    score: int = 0
    tps1 = time.time()
    for i in range(iter):
        if iter > 1:
            clear()
            print(f"Avancement : ", end=" ")
            compteur: int = math.ceil((i / iter) * 100)
            print("[" + compteur * "-" + ((100 - compteur) * " " + "]"))
        game = Gopher_Game(size=size, starting_player=starting)
        game.set_depth(depth)
        while game.final():
            #print(game)
            if game.get_player() == 1:
                play: Action = game.strategy_random()
                game.move(play)
                game.set_player(player=2)
            else:
                play: Action = game.strategy_negamax()
                game.move(play)
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
        f"Nombre d'itérations : {iter} | Taille de la grille : {size} | pronfondeur : {depth} | joueur de départ : {starting}"
    )
    print(f"Temps d'éxécution  : {temps:.4f} secondes")
    if iter > 1:
        print(f"Temps par partie  : {temps/iter:.4f} secondes")
    print(
        f"Nombre de parties gagnées pour le joueur 1: {score} {(score/iter)*100:.2f}%"
    )
    print(
        f"Nombre de parties gagnées pour le joueur 2: {iter-score} {((iter-score)/iter)*100:.2f}%"
    )

#debug()
test(iter=100, size=4,depth=12,starting=1)