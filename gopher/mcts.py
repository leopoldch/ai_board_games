import math
import random
from typing import List, Optional
from utils import *

class Node:
    def __init__(self, game, parent: Optional['Node'] = None, action: Optional[Action] = None) -> None:
        self.game = game
        self.parent: Node = parent
        self.action: Action = action
        self.children: List['Node'] = []
        self.visits: int = 0
        self.wins: int = 0

    def add_child(self, child: 'Node') -> None:
        self.children.append(child)

    def update(self, result: float) -> None:
        self.visits += 1
        self.wins += result

    def ucb1(self) -> float:
        coeff_value: float = 2
        if self.visits == 0:
            return float('inf')
        return self.wins / self.visits + math.sqrt(coeff_value * math.log(self.parent.visits) / self.visits)


class MCTS:
    def __init__(self, root_game, iterations: int = 1000) -> None:
        self.root = Node(root_game)
        self.iterations = iterations

    def search(self) -> Action:
        for _ in range(self.iterations):
            node = self.selection(self.root)
            if not node.game.final():
                self.expansion(node)
            result = self.simulation(node.game)
            self.backpropagation(node, result)

        if self.root.children:
            best_child = max(self.root.children, key=lambda child: child.visits)
            return best_child.action
        else:
            raise ValueError("No children found after MCTS iterations.")

    def selection(self, node: Node) -> Node:
        while node.children:
            node = max(node.children, key=lambda child: child.ucb1())
        return node

    def expansion(self, node: Node) -> None:
        game = node.game
        legal_moves = game.get_legits()
        if not legal_moves:  # Vérification si aucun mouvement légal n'est disponible
            return
        for move in legal_moves:
            new_game = game.copy()  # Copie légère de l'état du jeu
            new_game.move(move)
            new_game.set_player(3 - game.get_player())
            child = Node(new_game, parent=node, action=move)
            node.add_child(child)

    def simulation(self, game) -> float:
        while not game.final():  # Correction de la condition
            legal_moves: list[Cell] = game.get_legits()
            if not legal_moves:  # Pas de mouvements légaux disponibles
                break
            move: Cell = random.choice(legal_moves)
            game.move(move)
            game.set_player(3 - game.get_player())
        return game.score()

    def backpropagation(self, node: Node, result: float) -> None:
        while node:
            node.update(result)
            node = node.parent


def mcts(game) -> Action:
    mcts_search = MCTS(game)
    return mcts_search.search()
