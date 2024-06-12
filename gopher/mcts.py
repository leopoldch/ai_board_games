"""fichier pour la stratégie MCTS"""

import math
import random
from typing import List, Optional, Union

Environment = dict
Cell = tuple[int, int]
ActionGopher = Cell
ActionDodo = tuple[Cell, Cell]
Action = Union[ActionGopher, ActionDodo]
Player = int
State = list[tuple[Cell, Player]]
Score = int
Time = int
Grid = dict[Cell, Player]


class Node:
    """noeud de l'arbre MCTS"""

    def __init__(
        self,
        game,
        parent: Optional["Node"] = None,
        action: Optional[ActionGopher] = None,
    ) -> None:
        """constructeur du noeud"""
        self.game = game
        self.parent: Node = parent
        self.action: ActionGopher = action
        self.children: List["Node"] = []
        self.visits: int = 0
        self.wins: float = 0

    def add_child(self, child: "Node") -> None:
        """ajouter un enfant au noeud"""
        self.children.append(child)

    def update(self, result: float):
        """update le nombre de visite et/ou de win"""
        self.visits += 1
        self.wins += result

    def ucb1(self) -> float:
        """Permet de ne pas explorer les noeuds pas intéressants"""
        coeff_value: float = 2
        if self.visits == 0:
            return float("inf")
        return self.wins / self.visits + coeff_value * (
            math.sqrt(2 * math.log(self.parent.visits) / self.visits)
        )


class MCTS:
    """Classe pour la logique MCTS"""

    def __init__(self, root_game) -> None:
        """constructeur"""
        self.root = Node(root_game)

    def selection(self, node: Node) -> Node:
        """selection des noeuds"""
        while node.children:
            node = max(node.children, key=lambda child: child.ucb1())
        return node

    def expansion(self, node: Node) -> None:
        """expansion"""
        game = node.game
        legal_moves = game.get_legits()
        for move in legal_moves:
            tmp: dict = game.save_state()
            game.make_move(move)
            game.set_player(3 - game.get_player())
            child = Node(game, parent=node, action=move)
            node.add_child(child)
            game.restore_state(tmp)

    def simulation(self, game) -> float:
        """simulation"""
        state = game.save_state()
        while game.final():
            legal_moves = game.get_legits()
            move = random.choice(legal_moves)
            game.make_move(move)
            game.set_player(3 - game.get_player())
        result = game.score()
        game.restore_state(state)
        return result

    def backpropagation(self, node: Node, result: float) -> None:
        """backpropagation"""
        while node:
            node.update(result)
            node = node.parent

    def search(self, iterations: int) -> ActionGopher:
        """rechercher le meilleur coup"""
        for _ in range(iterations):
            node = self.selection(self.root)
            if node.game.final():
                self.expansion(node)
            result = self.simulation(node.game)
            self.backpropagation(node, result)

        if self.root.children:
            best_child = max(
                self.root.children,
                key=lambda child: (
                    child.wins / child.visits if child.visits != 0 else float("-inf")
                ),
            )
            return best_child.action
        raise ValueError("No children found after MCTS iterations.")


def mcts(game) -> ActionGopher:
    """stratégie MCTS"""
    mcts_search = MCTS(game)
    return mcts_search.search(1000)
